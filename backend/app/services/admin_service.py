"""
Admin Service
Business logic for admin operations
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Dict

from app.repositories.employee_repository import EmployeeRepository
from app.models.models import Employee, UserRole

class AdminService:
    """Handles admin operations business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.employee_repo = EmployeeRepository(db)
    
    def get_all_employees(self) -> List[Employee]:
        """Get all employees"""
        return self.employee_repo.get_all()
    
    def update_employee(
        self,
        emp_id: int,
        update_data: Dict,
        admin: Employee
    ) -> Dict:
        """
        Update employee details
        
        Args:
            emp_id: Employee database ID
            update_data: Fields to update
            admin: Admin performing update
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If validation fails
        """
        # Admin check already done in dependency, but we can verify role-specific logic here
        # Allowing HR to edit now
        
        # Get employee
        employee = self.employee_repo.get_by_db_id(emp_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Prevent immutable fields from being updated
        if 'emp_id' in update_data:
            del update_data['emp_id']
        if 'email' in update_data:
            del update_data['email']
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(employee, key) and value is not None:
                setattr(employee, key, value)
        
        self.db.commit()
        return {"message": "Employee updated successfully"}
    
    def delete_employee(self, emp_id: int, admin: Employee) -> Dict:
        """
        Delete employee
        
        Args:
            emp_id: Employee database ID
            admin: Admin performing deletion
            
        Returns:
            Success message
        """
        if admin.role == UserRole.HR:
            raise HTTPException(
                status_code=403,
                detail="HR cannot delete employees"
            )
        
        employee = self.employee_repo.get_by_db_id(emp_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        self.employee_repo.delete(employee)
        self.db.commit()
        
        return {"message": "Employee deleted successfully"}
    
    def _check_conflicts(self, current_id: int, update_data: Dict) -> bool:
        """Check for emp_id or email conflicts, excluding current employee"""
        if 'emp_id' in update_data:
            conflict = self.db.query(Employee).filter(
                Employee.id != current_id,
                Employee.emp_id == update_data['emp_id']
            ).first()
            if conflict:
                return True
        
        if 'email' in update_data:
            conflict = self.db.query(Employee).filter(
                Employee.id != current_id,
                Employee.email == update_data['email']
            ).first()
            if conflict:
                return True
        
        return False

    async def process_employee_master(self, file, admin: Employee) -> Dict:
        """Process uploaded employee master Excel file"""
        import pandas as pd
        import io
        
        # Admin check already done in dependency
        # Allowing HR to perform sync now
            
        content = await file.read()
        df = pd.read_excel(io.BytesIO(content))
        
        # Flexibly detect columns
        col_map = {
            'emp_id': ['emp_id', 'empid', 'employee id', 'id', 'employee code'],
            'full_name': ['full_name', 'name', 'employee name', 'fullname'],
            'email': ['email', 'email address', 'mail'],
            'designation': ['designation', 'role', 'position'],
            'phone_number': ['phone_number', 'phone', 'mobile', 'contact'],
            'first_name': ['first_name', 'firstname'],
            'last_name': ['last_name', 'lastname']
        }
        
        found_map = {}
        df_cols = [c.lower() for c in df.columns]
        
        for official, aliases in col_map.items():
            for i, col in enumerate(df.columns):
                if col.lower() in aliases:
                    found_map[official] = col
                    break
        
        if 'emp_id' not in found_map or 'email' not in found_map:
            raise HTTPException(status_code=400, detail="Missing critical columns: EmpId and Email are required.")
        
        saved = 0
        updated = 0
        
        from app.utils.file_utils import normalize_emp_id
        
        for _, row in df.iterrows():
            raw_id = str(row[found_map['emp_id']]).strip()
            if not raw_id or raw_id.lower() == 'nan': continue
            
            emp_id = normalize_emp_id(raw_id)
            
            email = str(row[found_map['email']]).strip()
            if not email or '@' not in email: continue
            
            existing = self.employee_repo.get_by_emp_id(emp_id) or self.employee_repo.get_by_email(email)
            
            data = {
                "full_name": row.get(found_map.get('full_name')),
                "email": email,
                "designation": row.get(found_map.get('designation')),
                "phone_number": str(row.get(found_map.get('phone_number'), '')),
                "first_name": row.get(found_map.get('first_name')),
                "last_name": row.get(found_map.get('last_name')),
                "status": "ACTIVE"
            }
            
            if existing:
                # Do not update email or emp_id for existing records
                update_fields = ["full_name", "designation", "phone_number", "status", "first_name", "last_name"]
                for key in update_fields:
                    if key in data and data[key] is not None:
                        setattr(existing, key, data[key])
                updated += 1
            else:
                data["emp_id"] = emp_id
                # Add default password hash for new imports
                from app.core.security import get_password_hash
                data["password_hash"] = get_password_hash("Test@123")
                data["is_verified"] = True
                self.employee_repo.create(data)
                saved += 1
                
        self.db.commit()
        return {"message": f"Sync complete. Created: {saved}, Updated: {updated}"}

    def generate_master_template(self) -> bytes:
        """Generate sample Excel template for employee master"""
        import pandas as pd
        import io
        
        df = pd.DataFrame(columns=['emp_id', 'full_name', 'email', 'designation', 'phone_number'])
        # Add a sample row
        df.loc[0] = ['RBIS0001', 'John Doe', 'john@rbistech.com', 'Software Engineer', '1234567890']
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Employees')
        return output.getvalue()
