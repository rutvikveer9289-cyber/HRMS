"""
Razorpay Payout API Endpoints
Handles real payment processing
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.api.dependencies.auth import get_current_user
from app.models.payroll import PayrollRecord as Payroll
from app.models.employee import Employee
from app.services.razorpay_service import get_razorpay_service

logger = logging.getLogger(__name__)

router = APIRouter()


class PayoutRequest(BaseModel):
    """Request model for single payout"""
    payroll_id: int
    mode: str = "IMPS"  # IMPS, NEFT, RTGS


class BulkPayoutRequest(BaseModel):
    """Request model for bulk payouts"""
    payroll_ids: List[int]
    mode: str = "IMPS"


class PayoutStatusRequest(BaseModel):
    """Request model to check payout status"""
    payout_id: str


@router.post("/payout/single")
def process_single_payout(
    request: PayoutRequest,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """
    Process a single payout via Razorpay
    
    - Requires HR/SUPER_ADMIN/CEO role
    - Transfers real money from your account to employee
    - Updates payroll status automatically
    """
    # Check permissions
    if current_user.role not in ['HR', 'SUPER_ADMIN', 'CEO']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only HR/Admin/CEO can process payments"
        )
    
    # Get payroll record
    payroll = db.query(Payroll).filter(Payroll.id == request.payroll_id).first()
    if not payroll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll record not found"
        )
    
    # Check if already paid
    if payroll.status == 'PAID':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This payroll has already been paid"
        )
    
    # Get employee details
    employee = db.query(Employee).filter(Employee.emp_id == payroll.emp_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Validate bank details
    if not employee.bank_account_no or not employee.bank_ifsc_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bank details not available for employee {employee.emp_id}"
        )
    
    try:
        # Get Razorpay service
        razorpay_service = get_razorpay_service()
        
        # Process payout
        result = razorpay_service.process_employee_payout(
            employee_data={
                'name': employee.full_name,
                'email': employee.email,
                'phone': employee.phone_number,
                'emp_id': employee.emp_id
            },
            bank_details={
                'account_number': employee.bank_account_no,
                'ifsc': employee.bank_ifsc_code,
                'name': employee.full_name
            },
            amount=float(payroll.net_salary),
            payroll_id=payroll.id,
            mode=request.mode
        )
        
        if result['success']:
            # Update payroll record
            payroll.status = 'PAID'
            payroll.payment_method = f"Razorpay {request.mode}"
            payroll.payment_date = result['created_at']
            payroll.transaction_id = result['payout_id']
            payroll.utr_number = result.get('utr')
            
            db.commit()
            
            logger.info(f"Payout successful for {employee.emp_id}: {result['payout_id']}")
            
            return {
                "success": True,
                "message": f"Payment of ₹{payroll.net_salary} processed successfully",
                "transaction_id": result['payout_id'],
                "utr": result.get('utr'),
                "status": result['status'],
                "emp_id": employee.emp_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Payout failed: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error(f"Error processing payout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment processing failed: {str(e)}"
        )


@router.post("/payout/bulk")
def process_bulk_payouts(
    request: BulkPayoutRequest,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """
    Process multiple payouts in bulk via Razorpay
    
    - Requires HR/SUPER_ADMIN/CEO role
    - Processes multiple payments simultaneously
    - Returns detailed results for each payment
    """
    # Check permissions
    if current_user.role not in ['HR', 'SUPER_ADMIN', 'CEO']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only HR/Admin/CEO can process payments"
        )
    
    # Get all payroll records
    payrolls = db.query(Payroll).filter(
        Payroll.id.in_(request.payroll_ids),
        Payroll.status != 'PAID'  # Only unpaid records
    ).all()
    
    if not payrolls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No unpaid payroll records found"
        )
    
    # Prepare data for bulk payout
    payout_data = []
    for payroll in payrolls:
        employee = db.query(Employee).filter(Employee.emp_id == payroll.emp_id).first()
        
        if not employee or not employee.bank_account_no or not employee.bank_ifsc_code:
            logger.warning(f"Skipping {payroll.emp_id}: Missing bank details")
            continue
        
        payout_data.append({
            'payroll_id': payroll.id,
            'emp_id': employee.emp_id,
            'employee_name': employee.full_name,
            'employee_email': employee.email,
            'employee_phone': employee.phone_number,
            'bank_account_no': employee.bank_account_no,
            'bank_ifsc': employee.bank_ifsc_code,
            'net_salary': float(payroll.net_salary)
        })
    
    if not payout_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid records to process (missing bank details)"
        )
    
    try:
        # Get Razorpay service
        razorpay_service = get_razorpay_service()
        
        # Process bulk payouts
        results = razorpay_service.process_bulk_payouts(payout_data, mode=request.mode)
        
        # Update database for successful payouts
        for detail in results['details']:
            if detail['success']:
                payroll = db.query(Payroll).filter(Payroll.id == detail['payroll_id']).first()
                if payroll:
                    payroll.status = 'PAID'
                    payroll.payment_method = f"Razorpay {request.mode}"
                    payroll.payment_date = detail['created_at']
                    payroll.transaction_id = detail['payout_id']
                    payroll.utr_number = detail.get('utr')
        
        db.commit()
        
        logger.info(f"Bulk payout completed: {results['successful']} successful, {results['failed']} failed")
        
        return {
            "success": True,
            "message": f"Processed {results['total']} payments: {results['successful']} successful, {results['failed']} failed",
            "total": results['total'],
            "successful": results['successful'],
            "failed": results['failed'],
            "details": results['details']
        }
        
    except Exception as e:
        logger.error(f"Error processing bulk payouts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk payment processing failed: {str(e)}"
        )


@router.post("/payout/status")
def check_payout_status(
    request: PayoutStatusRequest,
    current_user: Employee = Depends(get_current_user)
):
    """
    Check status of a payout
    
    - Returns current status of the transaction
    - Useful for tracking pending payments
    """
    try:
        razorpay_service = get_razorpay_service()
        status_info = razorpay_service.get_payout_status(request.payout_id)
        
        return {
            "success": True,
            **status_info
        }
        
    except Exception as e:
        logger.error(f"Error checking payout status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check status: {str(e)}"
        )


@router.get("/balance")
def get_account_balance(current_user: Employee = Depends(get_current_user)):
    """
    Get Razorpay account balance
    
    - Requires HR/SUPER_ADMIN/CEO role
    - Shows available balance for payouts
    """
    # Check permissions
    if current_user.role not in ['HR', 'SUPER_ADMIN', 'CEO']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only HR/Admin/CEO can view balance"
        )
    
    try:
        razorpay_service = get_razorpay_service()
        balance_info = razorpay_service.get_account_balance()
        
        return {
            "success": True,
            **balance_info
        }
        
    except Exception as e:
        logger.error(f"Error fetching balance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch balance: {str(e)}"
        )


@router.get("/test-connection")
def test_razorpay_connection(current_user: Employee = Depends(get_current_user)):
    """
    Test Razorpay API connection
    
    - Verifies API credentials are working
    - Checks account status
    """
    # Check permissions
    if current_user.role not in ['HR', 'SUPER_ADMIN', 'CEO']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only HR/Admin/CEO can test connection"
        )
    
    try:
        razorpay_service = get_razorpay_service()
        balance_info = razorpay_service.get_account_balance()
        
        return {
            "success": True,
            "message": "Razorpay connection successful",
            "mode": razorpay_service.mode,
            "balance": balance_info['balance'],
            "currency": balance_info['currency']
        }
        
    except Exception as e:
        logger.error(f"Razorpay connection test failed: {str(e)}")
        return {
            "success": False,
            "message": "Razorpay connection failed",
            "error": str(e)
        }
