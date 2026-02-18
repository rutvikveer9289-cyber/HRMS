"""
Attendance Service
Business logic for attendance management and file processing
"""
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from typing import List, Dict
import logging
from datetime import date, datetime, timedelta

from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.file_repository import FileRepository
from app.models.models import Employee, UserRole
from app.utils.file_utils import calculate_file_hash, generate_safe_filename, normalize_emp_id
from app.utils.date_utils import parse_date, format_time
from app.services.cleaner import detect_and_clean_memory
from app.services.azure_storage_service import upload_bytes_to_azure_sync

logger = logging.getLogger(__name__)

class AttendanceService:
    """Handles attendance business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.attendance_repo = AttendanceRepository(db)
        self.file_repo = FileRepository(db)
        from app.repositories.employee_repository import EmployeeRepository
        self.employee_repo = EmployeeRepository(db)
    
    def process_uploaded_files(
        self,
        files: List[UploadFile],
        admin: Employee
    ) -> Dict:
        """
        Process uploaded attendance files
        
        Args:
            files: List of uploaded files
            admin: Admin user uploading files
            
        Returns:
            Dictionary with processing results
        """
        results = []
        
        for file in files:
            logger.info(f"Received file for processing: {file.filename}")
            try:
                # We use a nested transaction/savepoint if possible, or just commit sequentially
                result = self._process_single_file(file, admin)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {e}", exc_info=True)
                # Ensure we at least roll back any partial attendance records, 
                # but we want to keep the file log if it was committed.
                self.db.rollback() 
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "reason": str(e)
                })
        
        return {"message": "Upload processing complete", "results": results}
    
    def _process_single_file(
        self,
        file: UploadFile,
        admin: Employee
    ) -> Dict:
        """
        Process a single attendance file
        """
        # Read file content
        content = file.file.read()
        
        # Calculate hash for duplicate detection
        file_hash = calculate_file_hash(content)
        existing_file = self.file_repo.get_by_hash(file_hash)
        
        # Try to use pre-cleaned data if available
        if hasattr(file, 'cleaned_data') and file.cleaned_data:
            cleaned_data = file.cleaned_data
            detected_type = getattr(file, 'detected_type', "In/Out Duration Report")
        else:
            cleaned_data, detected_type = detect_and_clean_memory(content)
        
        if not cleaned_data:
            return {
                "filename": file.filename,
                "status": "error",
                "reason": detected_type
            }

        # 1. PRE-VALIDATION: Check pattern
        import re
        for i, rec in enumerate(cleaned_data):
            raw_id = rec.get('EmpID', '')
            emp_id = normalize_emp_id(raw_id)
            if not re.match(r'^RBIS\d{4}$', emp_id):
                return {
                    "filename": file.filename,
                    "status": "error",
                    "reason": f"Data Validation Error: Row {i+1} has invalid ID format '{raw_id}'"
                }

        # 2. FILE LOGGING (Commit this first)
        if not existing_file:
            safe_filename = generate_safe_filename(file.filename)
            log_data = {
                "filename": file.filename,
                "uploaded_by": admin.email,
                "report_type": detected_type,
                "file_hash": file_hash,
                "file_path": safe_filename
            }
            self.file_repo.create(log_data)
            self.db.commit() # Commit file log separately
            
            # AZURE UPLOAD
            try:
                upload_bytes_to_azure_sync(content, safe_filename, getattr(file, 'content_type', "application/octet-stream"))
            except Exception as e:
                logger.warning(f"Azure backup failed: {e}")
        else:
            logger.info(f"Using existing upload record for {file.filename}")
        
        # 3. DATABASE PROCESSING (Attendance Records)
        try:
            saved_count, updated_count = self._process_attendance_records(
                cleaned_data,
                file.filename
            )
            
            self.db.commit()
            return {
                "filename": file.filename,
                "status": "success",
                "type": detected_type,
                "details": f"Processed {len(cleaned_data)} records (Saved: {saved_count}, Updated: {updated_count})"
            }
        except Exception as e:
            logger.error(f"Database error processing records for {file.filename}: {e}")
            self.db.rollback()
            return {
                "filename": file.filename,
                "status": "error",
                "reason": f"Database processing error: {str(e)}"
            }
    
    def _process_attendance_records(
        self,
        cleaned_data: List[Dict],
        source_filename: str
    ) -> tuple:
        """Process attendance records with employee existence check"""
        saved_count = 0
        updated_count = 0
        
        for rec in cleaned_data:
            raw_id = str(rec.get('EmpID', '')).strip()
            emp_id = normalize_emp_id(raw_id)
            if not emp_id: continue
            
            # Check if employee exists in system (Foreign Key requirement)
            if not self.employee_repo.get_by_emp_id(emp_id):
                continue

            date_val = rec.get('Date')
            date_obj = parse_date(date_val)
            if not date_obj: continue
            
            existing = self.attendance_repo.get_by_emp_and_date(emp_id, date_obj)
            
            record_data = {
                "first_in": format_time(rec.get('First_In')),
                "last_out": format_time(rec.get('Last_Out')),
                "in_duration": format_time(rec.get('In_Duration')),
                "out_duration": format_time(rec.get('Out_Duration')),
                "total_duration": format_time(rec.get('Total_Duration')),
                "punch_records": rec.get('Punch_Records'),
                "attendance_status": rec.get('Attendance'),
                "source_file": source_filename
            }
            
            if existing:
                if existing.attendance_status == "On Leave" and record_data["attendance_status"] == "Absent":
                    record_data["attendance_status"] = "On Leave"
                self.attendance_repo.update(existing, record_data)
                updated_count += 1
            else:
                record_data.update({"emp_id": emp_id, "date": date_obj})
                self.attendance_repo.create(record_data)
                saved_count += 1
        
        return saved_count, updated_count
    
    def get_attendance_records(
        self, 
        user: Employee, 
        start_date_str: Optional[str] = None, 
        end_date_str: Optional[str] = None
    ) -> List:
        """
        Get attendance records with optional date range
        Defaults to last 180 days if no range provided
        """
        # Parse or calculate dates
        today = date.today()
        
        if start_date_str:
            start_date = parse_date(start_date_str)
        else:
            start_date = today - timedelta(days=180)
            
        if end_date_str:
            end_date = parse_date(end_date_str)
        else:
            end_date = today
        
        if user.role == UserRole.EMPLOYEE:
            records = self.attendance_repo.get_by_date_range(
                emp_id=user.emp_id,
                start_date=start_date,
                end_date=end_date
            )
        else:
            records = self.attendance_repo.get_by_date_range(
                start_date=start_date,
                end_date=end_date
            )
            
        # Enrich and flatten for frontend
        result = []
        for r in records:
            data = {c.name: getattr(r, c.name) for c in r.__table__.columns}
            # Support both date objects and ISO strings
            if isinstance(data['date'], (date, datetime)):
                data['date'] = data['date'].isoformat()
            
            # Resolve name (owner relationship takes priority)
            data['employee_name'] = r.owner.full_name if r.owner else "Unknown"
            result.append(data)
            
        return result
    
    def update_attendance_record(
        self,
        attendance_id: int,
        update_data: Dict
    ) -> Dict:
        """
        Update attendance record
        
        Args:
            attendance_id: Attendance record ID
            update_data: Fields to update
            
        Returns:
            Updated record data
            
        Raises:
            HTTPException: If record not found
        """
        record = self.attendance_repo.get_by_id(attendance_id)
        
        if not record:
            raise HTTPException(status_code=404, detail="Attendance record not found")
        
        # Update record
        self.attendance_repo.update(record, update_data)
        self.attendance_repo.commit()
        
        return {"message": "Attendance record updated successfully"}

    def delete_attendance_record(self, attendance_id: int) -> Dict:
        """
        Delete attendance record
        
        Args:
            attendance_id: Attendance record ID
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If record not found
        """
        record = self.attendance_repo.get_by_id(attendance_id)
        if not record:
            raise HTTPException(status_code=404, detail="Attendance record not found")
        
        self.attendance_repo.delete(record)
        self.attendance_repo.commit()
        
        return {"message": "Attendance record deleted successfully"}
