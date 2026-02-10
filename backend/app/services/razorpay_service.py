"""
Razorpay Payout Service
Handles real money transfers to employee bank accounts
"""

import razorpay
from typing import Dict, List, Optional
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RazorpayPayoutService:
    """Service for processing real payments via Razorpay"""
    
    def __init__(self):
        """Initialize Razorpay client with credentials from environment"""
        self.key_id = os.getenv('RAZORPAY_KEY_ID')
        self.key_secret = os.getenv('RAZORPAY_KEY_SECRET')
        self.account_number = os.getenv('RAZORPAY_ACCOUNT_NUMBER')
        self.mode = os.getenv('RAZORPAY_MODE', 'test')
        
        if not self.key_id or not self.key_secret:
            raise ValueError("Razorpay credentials not configured in environment variables")
        
        # Initialize Razorpay client
        self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
        
        logger.info(f"Razorpay Payout Service initialized in {self.mode} mode")
    
    def create_contact(self, employee_data: Dict) -> str:
        """
        Create a contact in Razorpay for the employee
        
        Args:
            employee_data: Dict containing employee details
                - name: Employee full name
                - email: Employee email
                - phone: Employee phone number
                - emp_id: Employee ID
        
        Returns:
            contact_id: Razorpay contact ID
        """
        try:
            contact = self.client.contact.create({
                "name": employee_data['name'],
                "email": employee_data.get('email', ''),
                "contact": employee_data.get('phone', ''),
                "type": "employee",
                "reference_id": employee_data['emp_id'],
                "notes": {
                    "employee_id": employee_data['emp_id']
                }
            })
            
            logger.info(f"Contact created for employee {employee_data['emp_id']}: {contact['id']}")
            return contact['id']
            
        except Exception as e:
            logger.error(f"Error creating contact for {employee_data['emp_id']}: {str(e)}")
            raise
    
    def create_fund_account(self, contact_id: str, bank_details: Dict) -> str:
        """
        Create a fund account (bank account) for the contact
        
        Args:
            contact_id: Razorpay contact ID
            bank_details: Dict containing bank information
                - account_number: Bank account number
                - ifsc: IFSC code
                - name: Account holder name
        
        Returns:
            fund_account_id: Razorpay fund account ID
        """
        try:
            fund_account = self.client.fund_account.create({
                "contact_id": contact_id,
                "account_type": "bank_account",
                "bank_account": {
                    "name": bank_details['name'],
                    "ifsc": bank_details['ifsc'],
                    "account_number": bank_details['account_number']
                }
            })
            
            logger.info(f"Fund account created: {fund_account['id']}")
            return fund_account['id']
            
        except Exception as e:
            logger.error(f"Error creating fund account: {str(e)}")
            raise
    
    def create_payout(
        self,
        fund_account_id: str,
        amount: float,
        currency: str = "INR",
        mode: str = "IMPS",
        purpose: str = "salary",
        reference_id: Optional[str] = None,
        narration: Optional[str] = None
    ) -> Dict:
        """
        Create a payout (transfer money)
        
        Args:
            fund_account_id: Razorpay fund account ID
            amount: Amount in rupees (will be converted to paise)
            currency: Currency code (default: INR)
            mode: Transfer mode (IMPS/NEFT/RTGS)
            purpose: Purpose of payment (salary/bonus/reimbursement)
            reference_id: Your internal reference ID
            narration: Description for bank statement
        
        Returns:
            Dict containing payout details including transaction ID
        """
        try:
            # Convert rupees to paise (Razorpay uses smallest currency unit)
            amount_paise = int(amount * 100)
            
            payout_data = {
                "account_number": self.account_number,
                "fund_account_id": fund_account_id,
                "amount": amount_paise,
                "currency": currency,
                "mode": mode,
                "purpose": purpose,
                "queue_if_low_balance": True,  # Queue if insufficient balance
                "reference_id": reference_id or f"payout_{datetime.now().timestamp()}",
                "narration": narration or "Salary Payment"
            }
            
            payout = self.client.payout.create(payout_data)
            
            logger.info(f"Payout created: {payout['id']} for amount ₹{amount}")
            
            return {
                'payout_id': payout['id'],
                'status': payout['status'],
                'utr': payout.get('utr'),  # Unique Transaction Reference
                'amount': amount,
                'mode': mode,
                'created_at': payout['created_at']
            }
            
        except Exception as e:
            logger.error(f"Error creating payout: {str(e)}")
            raise
    
    def get_payout_status(self, payout_id: str) -> Dict:
        """
        Get status of a payout
        
        Args:
            payout_id: Razorpay payout ID
        
        Returns:
            Dict containing payout status and details
        """
        try:
            payout = self.client.payout.fetch(payout_id)
            
            return {
                'payout_id': payout['id'],
                'status': payout['status'],  # queued/pending/processing/processed/reversed/cancelled
                'utr': payout.get('utr'),
                'amount': payout['amount'] / 100,  # Convert paise to rupees
                'mode': payout['mode'],
                'failure_reason': payout.get('failure_reason')
            }
            
        except Exception as e:
            logger.error(f"Error fetching payout status: {str(e)}")
            raise
    
    def process_employee_payout(
        self,
        employee_data: Dict,
        bank_details: Dict,
        amount: float,
        payroll_id: int,
        mode: str = "IMPS"
    ) -> Dict:
        """
        Complete flow: Create contact, fund account, and process payout
        
        Args:
            employee_data: Employee information
            bank_details: Bank account details
            amount: Amount to transfer
            payroll_id: Internal payroll record ID
            mode: Transfer mode
        
        Returns:
            Dict containing transaction details
        """
        try:
            # Step 1: Create or get contact
            contact_id = self.create_contact(employee_data)
            
            # Step 2: Create or get fund account
            fund_account_id = self.create_fund_account(contact_id, bank_details)
            
            # Step 3: Create payout
            payout_result = self.create_payout(
                fund_account_id=fund_account_id,
                amount=amount,
                mode=mode,
                purpose="salary",
                reference_id=f"payroll_{payroll_id}",
                narration=f"Salary for {employee_data['emp_id']}"
            )
            
            return {
                'success': True,
                'contact_id': contact_id,
                'fund_account_id': fund_account_id,
                **payout_result
            }
            
        except Exception as e:
            logger.error(f"Error processing employee payout: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_bulk_payouts(
        self,
        payroll_records: List[Dict],
        mode: str = "IMPS"
    ) -> Dict:
        """
        Process multiple payouts in bulk
        
        Args:
            payroll_records: List of dicts containing employee and payment info
            mode: Transfer mode
        
        Returns:
            Dict containing success/failure counts and details
        """
        results = {
            'total': len(payroll_records),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for record in payroll_records:
            try:
                result = self.process_employee_payout(
                    employee_data={
                        'name': record['employee_name'],
                        'email': record.get('employee_email'),
                        'phone': record.get('employee_phone'),
                        'emp_id': record['emp_id']
                    },
                    bank_details={
                        'account_number': record['bank_account_no'],
                        'ifsc': record['bank_ifsc'],
                        'name': record['employee_name']
                    },
                    amount=record['net_salary'],
                    payroll_id=record['payroll_id'],
                    mode=mode
                )
                
                if result['success']:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                
                results['details'].append({
                    'emp_id': record['emp_id'],
                    'payroll_id': record['payroll_id'],
                    **result
                })
                
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'emp_id': record['emp_id'],
                    'payroll_id': record['payroll_id'],
                    'success': False,
                    'error': str(e)
                })
        
        logger.info(f"Bulk payout completed: {results['successful']} successful, {results['failed']} failed")
        return results
    
    def get_account_balance(self) -> Dict:
        """
        Get Razorpay account balance
        
        Returns:
            Dict containing balance information
        """
        try:
            balance = self.client.account.balance()
            
            return {
                'balance': balance['balance'] / 100,  # Convert paise to rupees
                'currency': balance['currency']
            }
            
        except Exception as e:
            logger.error(f"Error fetching account balance: {str(e)}")
            raise
    
    def verify_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        """
        Verify webhook signature from Razorpay
        
        Args:
            payload: Webhook payload
            signature: Signature from Razorpay
            secret: Webhook secret
        
        Returns:
            bool: True if signature is valid
        """
        try:
            return self.client.utility.verify_webhook_signature(payload, signature, secret)
        except Exception as e:
            logger.error(f"Webhook verification failed: {str(e)}")
            return False


# Singleton instance
_razorpay_service = None


def get_razorpay_service() -> RazorpayPayoutService:
    """Get or create Razorpay service instance"""
    global _razorpay_service
    if _razorpay_service is None:
        _razorpay_service = RazorpayPayoutService()
    return _razorpay_service
