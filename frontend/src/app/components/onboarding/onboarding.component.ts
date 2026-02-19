import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AttendanceService } from '../../services/attendance.service';
import { AdminService } from '../../services/admin.service';
import { NotificationService } from '../../services/notification.service';
import { AuthService } from '../../services/auth.service';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-onboarding',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './onboarding.component.html',
  styleUrls: ['./onboarding.component.css']
})
export class OnboardingComponent implements OnInit {
  employee = {
    first_name: '',
    last_name: '',
    full_name: '',
    phone_number: '',
    email: '',
    designation: '',
    emp_id: ''
  };

  documents = [
    { name: 'Identity Proof (Aadhar/Voter ID)', key: 'id_proof', file: null, uploaded: false },
    { name: 'Address Proof', key: 'address_proof', file: null, uploaded: false },
    { name: 'Educational Certificates', key: 'education', file: null, uploaded: false },
    { name: 'Previous Employment Records', key: 'experience', file: null, uploaded: false }
  ];

  loading = false;
  uploadingMaster = false;
  canSync = false;

  constructor(
    private attendanceService: AttendanceService,
    private adminService: AdminService,
    private notificationService: NotificationService,
    public authService: AuthService
  ) { }

  ngOnInit() {
    const role = this.authService.getUserRole();
    this.canSync = role === 'SUPER_ADMIN' || role === 'CEO';
    this.suggestNextId();
  }

  suggestNextId() {
    this.attendanceService.getNextId().subscribe({
      next: (res) => {
        this.employee.emp_id = res.next_id;
      },
      error: () => {
        this.notificationService.showAlert('Error fetching next ID', 'error');
      }
    });
  }

  onNameChange() {
    // Auto-update full name
    this.employee.full_name = `${this.employee.first_name} ${this.employee.last_name}`.trim();

    // Auto-suggest email: firstname + lastname[0] + @rbistech.com
    if (this.employee.first_name && this.employee.last_name) {
      const first = this.employee.first_name.toLowerCase().trim();
      const lastChar = this.employee.last_name.trim().charAt(0).toLowerCase();
      this.employee.email = `${first}${lastChar}@rbistech.com`;
    }
  }

  onSubmit() {
    if (this.employee.emp_id && !this.employee.emp_id.toLowerCase().startsWith('rbis')) {
      this.notificationService.showAlert('Employee ID should start with "RBIS"', 'info');
    }

    this.loading = true;

    // Create FormData for file upload support
    const formData = new FormData();
    formData.append('emp_id', this.employee.emp_id);
    formData.append('full_name', this.employee.full_name);
    formData.append('first_name', this.employee.first_name);
    formData.append('last_name', this.employee.last_name);
    formData.append('phone_number', this.employee.phone_number);
    formData.append('designation', this.employee.designation);
    formData.append('email', this.employee.email);

    // Append documents if they exist
    this.documents.forEach(doc => {
      if (doc.file) {
        formData.append(doc.key, doc.file);
      }
    });

    this.attendanceService.onboardEmployee(formData).subscribe({
      next: (res) => {
        this.loading = false;
        this.notificationService.showAlert(res.message, 'success');
        this.resetForm();
        this.suggestNextId();
      },
      error: (err) => {
        this.loading = false;
        const msg = err.error?.detail || 'Onboarding failed';
        this.notificationService.showAlert(msg, 'error');
      }
    });
  }

  downloadTemplate() {
    this.adminService.downloadTemplate().subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'Employee_Master_Template.xlsx';
        link.click();
        window.URL.revokeObjectURL(url);
      },
      error: () => this.notificationService.showAlert('Failed to download template', 'error')
    });
  }

  onEmployeeMasterSelected(event: any) {
    const file: File = event.target.files[0];
    if (file) {
      this.uploadingMaster = true;
      this.adminService.uploadEmployeeMaster(file).subscribe({
        next: (res: any) => {
          this.uploadingMaster = false;
          this.notificationService.showAlert(res.message, 'success');
          this.suggestNextId();
          event.target.value = '';
        },
        error: (err: any) => {
          this.uploadingMaster = false;
          const errorMsg = err.error?.detail || 'Error uploading employee master.';
          this.notificationService.showAlert(errorMsg, 'error');
          event.target.value = '';
        }
      });
    }
  }

  onlyNumbers(event: KeyboardEvent): boolean {
    const charCode = event.which ? event.which : event.keyCode;
    // Allow: backspace, delete, tab, escape, enter
    if ([8, 9, 27, 13].indexOf(charCode) !== -1 ||
      // Allow: Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
      (charCode === 65 && event.ctrlKey === true) ||
      (charCode === 67 && event.ctrlKey === true) ||
      (charCode === 86 && event.ctrlKey === true) ||
      (charCode === 88 && event.ctrlKey === true)) {
      return true;
    }
    // Ensure that it is a number and stop the keypress
    if (charCode < 48 || charCode > 57) {
      event.preventDefault();
      return false;
    }
    return true;
  }

  onFileSelected(event: any, doc: any) {
    const file = event.target.files[0];
    if (file) {
      doc.file = file;
      doc.uploaded = true;
      this.notificationService.showAlert(`${doc.name} selected`, 'info');
    }
  }

  removeFile(doc: any) {
    doc.file = null;
    doc.uploaded = false;
  }

  resetForm() {
    this.employee = {
      first_name: '',
      last_name: '',
      full_name: '',
      phone_number: '',
      email: '',
      designation: '',
      emp_id: ''
    };
    this.documents.forEach(d => {
      d.file = null;
      d.uploaded = false;
    });
  }
}
