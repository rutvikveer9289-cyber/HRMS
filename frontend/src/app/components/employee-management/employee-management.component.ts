import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminService } from '../../services/admin.service';
import { NotificationService } from '../../services/notification.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-employee-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './employee-management.component.html',
  styleUrls: ['./employee-management.component.css']
})
export class EmployeeManagementComponent implements OnInit {
  employees: any[] = [];
  filteredEmployees: any[] = [];
  searchTerm: string = '';
  editingEmployee: any = null;
  canEdit: boolean = false;

  // Document Management
  isDocModalOpen: boolean = false;
  selectedEmployeeDocs: any[] = [];
  activeEmployee: any = null;
  isDocUploading: boolean = false;
  docTypes = [
    { key: 'id_proof', label: 'Identity Proof' },
    { key: 'address_proof', label: 'Address Proof' },
    { key: 'education', label: 'Educational Certificates' },
    { key: 'experience', label: 'Previous Employment Records' }
  ];

  constructor(
    private adminService: AdminService,
    private notificationService: NotificationService,
    private authService: AuthService
  ) { }

  ngOnInit(): void {
    const role = this.authService.getUserRole();
    this.canEdit = role === 'SUPER_ADMIN' || role === 'CEO' || role === 'HR';
    this.loadEmployees();
  }

  loadEmployees(): void {
    this.adminService.getEmployees().subscribe({
      next: (data) => {
        this.employees = data.sort((a, b) => {
          const idA = a.emp_id || '';
          const idB = b.emp_id || '';
          return idA.localeCompare(idB, undefined, { numeric: true, sensitivity: 'base' });
        });
        this.filterEmployees();
      },
      error: (err) => this.notificationService.showAlert('Failed to load employees', 'error')
    });
  }

  filterEmployees(): void {
    if (!this.searchTerm) {
      this.filteredEmployees = this.employees;
    } else {
      const term = this.searchTerm.toLowerCase();

      // Normalize term if it's a number or simple RBIS format
      let normalizedTerm = term;
      if (term.startsWith('rbis')) {
        const num = term.replace('rbis', '').replace(/^0+/, '');
        if (num) normalizedTerm = 'rbis' + num.padStart(4, '0');
      } else if (!isNaN(Number(term))) {
        normalizedTerm = 'rbis' + term.padStart(4, '0');
      }

      this.filteredEmployees = this.employees.filter(e =>
        (e.full_name && e.full_name.toLowerCase().includes(term)) ||
        (e.emp_id && e.emp_id.toLowerCase() === normalizedTerm) ||
        (e.emp_id && e.emp_id.toLowerCase().includes(term)) ||
        (e.email && e.email.toLowerCase().includes(term)) ||
        (e.phone_number && e.phone_number.toLowerCase().includes(term)) ||
        (e.designation && e.designation.toLowerCase().includes(term))
      );
    }
  }

  editEmployee(emp: any): void {
    this.editingEmployee = { ...emp };
  }

  cancelEdit(): void {
    this.editingEmployee = null;
  }

  saveEmployee(): void {
    if (this.editingEmployee) {
      this.adminService.updateEmployee(this.editingEmployee.id, this.editingEmployee).subscribe({
        next: () => {
          this.notificationService.showAlert('Employee updated successfully', 'success');
          this.editingEmployee = null;
          this.loadEmployees();
        },
        error: (err) => this.notificationService.showAlert(err.error?.detail || 'Update failed', 'error')
      });
    }
  }

  deleteEmployee(id: number): void {
    if (confirm('Are you sure you want to delete this employee? Information will be permanently removed.')) {
      this.adminService.deleteEmployee(id).subscribe({
        next: () => {
          this.notificationService.showAlert('Employee record deleted', 'success');
          this.loadEmployees();
        },
        error: (err) => this.notificationService.showAlert('Delete failed', 'error')
      });
    }
  }

  // --- Document Management Methods ---

  manageDocuments(emp: any): void {
    this.activeEmployee = emp;
    this.isDocModalOpen = true;
    this.loadEmployeeDocuments();
  }

  closeDocModal(): void {
    this.isDocModalOpen = false;
    this.activeEmployee = null;
    this.selectedEmployeeDocs = [];
  }

  loadEmployeeDocuments(): void {
    if (!this.activeEmployee) return;
    this.adminService.getEmployeeDocuments(this.activeEmployee.emp_id).subscribe({
      next: (docs) => this.selectedEmployeeDocs = docs,
      error: () => this.notificationService.showAlert('Failed to load documents', 'error')
    });
  }

  uploadDoc(event: any, docType: string): void {
    const file = event.target.files[0];
    if (!file || !this.activeEmployee) return;

    this.isDocUploading = true;
    this.adminService.uploadEmployeeDocument(this.activeEmployee.emp_id, docType, file).subscribe({
      next: () => {
        this.isDocUploading = false;
        this.notificationService.showAlert('Document uploaded successfully', 'success');
        this.loadEmployeeDocuments();
        event.target.value = '';
      },
      error: (err) => {
        this.isDocUploading = false;
        this.notificationService.showAlert(err.error?.detail || 'Upload failed', 'error');
      }
    });
  }

  deleteDoc(docId: number): void {
    if (!confirm('Are you sure you want to delete this document?')) return;
    this.adminService.deleteEmployeeDocument(docId).subscribe({
      next: () => {
        this.notificationService.showAlert('Document removed', 'success');
        this.loadEmployeeDocuments();
      },
      error: () => this.notificationService.showAlert('Delete failed', 'error')
    });
  }

  hasDoc(type: string): boolean {
    return this.selectedEmployeeDocs.some(d => d.document_type === type);
  }

  getDocName(type: string): string {
    const doc = this.selectedEmployeeDocs.find(d => d.document_type === type);
    return doc ? doc.document_name : '';
  }

  getDocId(type: string): number {
    const doc = this.selectedEmployeeDocs.find(d => d.document_type === type);
    return doc ? doc.id : 0;
  }
}
