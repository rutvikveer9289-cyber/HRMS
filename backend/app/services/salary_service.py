"""
Salary Service
Business logic for salary structure management
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.salary_repository import SalaryRepository
from decimal import Decimal
from datetime import date
import logging

logger = logging.getLogger(__name__)

class SalaryService:
    """Handles salary structure business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.salary_repo = SalaryRepository(db)
        self.employee_repo = EmployeeRepository(db)
    
    def create_salary_structure(self, emp_id: str, salary_data: dict, created_by: str) -> dict:
        """
        Create new salary structure for employee
        
        Args:
            emp_id: Employee ID
            salary_data: Salary components
            created_by: User creating the structure
            
        Returns:
            Created salary structure
        """
        # Validate Employee Validation
        if not self.employee_repo.exists_by_emp_id(emp_id):
            raise HTTPException(status_code=404, detail=f"Employee with ID {emp_id} not found")

        try:
            # Calculate gross salary
            gross_salary = self._calculate_gross_salary(salary_data)
            
            # Deactivate previous salary structures
            effective_from = salary_data.get('effective_from') or date.today()
            self.salary_repo.deactivate_previous(emp_id, effective_from)
            
            # Create new structure
            new_salary = {
                "emp_id": emp_id,
                "basic_salary": Decimal(str(salary_data['basic_salary'])),
                "hra": Decimal(str(salary_data.get('hra', 0))),
                "transport_allowance": Decimal(str(salary_data.get('transport_allowance', 0))),
                "dearness_allowance": Decimal(str(salary_data.get('dearness_allowance', 0))),
                "medical_allowance": Decimal(str(salary_data.get('medical_allowance', 0))),
                "special_allowance": Decimal(str(salary_data.get('special_allowance', 0))),
                "other_allowances": Decimal(str(salary_data.get('other_allowances', 0))),
                "gross_salary": gross_salary,
                "effective_from": effective_from,
                "is_active": True,
                "created_by": created_by
            }
            
            return self.salary_repo.create(new_salary)
        except Exception as e:
            logger.error(f"Error creating salary structure: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create salary structure: {str(e)}")
    
    def get_active_salary(self, emp_id: str):
        """Get active salary structure for employee"""
        salary = self.salary_repo.get_active_by_emp_id(emp_id)
        if not salary:
            raise HTTPException(status_code=404, detail="No active salary structure found for employee")
        return salary
    
    def get_salary_history(self, emp_id: str):
        """Get salary history for employee"""
        return self.salary_repo.get_history_by_emp_id(emp_id)
    
    def update_salary_structure(self, salary_id: int, salary_data: dict):
        """Update existing salary structure"""
        salary = self.salary_repo.get_by_id(salary_id)
        if not salary:
            raise HTTPException(status_code=404, detail="Salary structure not found")
        
        # Update fields
        if 'basic_salary' in salary_data:
            salary.basic_salary = Decimal(str(salary_data['basic_salary']))
        if 'hra' in salary_data:
            salary.hra = Decimal(str(salary_data['hra']))
        if 'transport_allowance' in salary_data:
            salary.transport_allowance = Decimal(str(salary_data['transport_allowance']))
        if 'dearness_allowance' in salary_data:
            salary.dearness_allowance = Decimal(str(salary_data['dearness_allowance']))
        if 'medical_allowance' in salary_data:
            salary.medical_allowance = Decimal(str(salary_data['medical_allowance']))
        if 'special_allowance' in salary_data:
            salary.special_allowance = Decimal(str(salary_data['special_allowance']))
        if 'other_allowances' in salary_data:
            salary.other_allowances = Decimal(str(salary_data['other_allowances']))
        
        # Recalculate gross salary
        salary.gross_salary = (
            salary.basic_salary + salary.hra + salary.transport_allowance +
            salary.dearness_allowance + salary.medical_allowance +
            salary.special_allowance + salary.other_allowances
        )
        
        return self.salary_repo.update(salary)
    
    def _calculate_gross_salary(self, salary_data: dict) -> Decimal:
        """Calculate gross salary from components"""
        basic = Decimal(str(salary_data.get('basic_salary', 0)))
        hra = Decimal(str(salary_data.get('hra', 0)))
        transport = Decimal(str(salary_data.get('transport_allowance', 0)))
        dearness = Decimal(str(salary_data.get('dearness_allowance', 0)))
        medical = Decimal(str(salary_data.get('medical_allowance', 0)))
        special = Decimal(str(salary_data.get('special_allowance', 0)))
        other = Decimal(str(salary_data.get('other_allowances', 0)))
        
        return basic + hra + transport + dearness + medical + special + other
