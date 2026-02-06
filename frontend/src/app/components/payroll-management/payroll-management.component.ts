import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PayrollService } from '../../services/payroll.service';
import { SalaryService } from '../../services/salary.service';
import { OvertimeService } from '../../services/overtime.service';
import { AuthService } from '../../services/auth.service';
import { DeductionService } from '../../services/deduction.service';

@Component({
  selector: 'app-payroll-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './payroll-management.component.html',
  styleUrls: ['./payroll-management.component.css']
})
export class PayrollManagementComponent implements OnInit {
  activeTab: string = 'payroll';

  // Access Control
  canManagePayroll: boolean = false;
  currentUser: any = null;

  // Payroll data
  selectedMonth: number = new Date().getMonth() + 1;
  selectedYear: number = new Date().getFullYear();
  payrollRecords: any[] = [];
  myPayslips: any[] = []; // For employee view
  activeSalary: any = null; // For employee view
  loading: boolean = false;
  processSingleEmpId: string = '';
  paymentMethods: string[] = ['Bank Transfer', 'Cash', 'Check', 'UPI'];

  // Deduction data
  deductionTypes: any[] = [];
  employeeDeductions: any[] = [];
  deductionForm: any = {
    emp_id: '',
    deduction_type_id: null,
    calculation_type: 'FIXED',
    value: 0,
    effective_from: new Date().toISOString().split('T')[0]
  };
  newDeductionType: any = {
    name: '',
    description: '',
    calculation_type: 'FIXED',
    default_value: 0
  };

  // Salary data
  salaryForm: any = {
    emp_id: '',
    basic_salary: 0,
    hra: 0,
    transport_allowance: 0,
    dearness_allowance: 0,
    medical_allowance: 0,
    special_allowance: 0,
    other_allowances: 0
  };

  // Overtime data
  overtimeRecords: any[] = [];
  pendingOvertimeApprovals: any[] = [];

  constructor(
    private payrollService: PayrollService,
    private salaryService: SalaryService,
    private overtimeService: OvertimeService,
    private authService: AuthService,
    private deductionService: DeductionService
  ) { }

  ngOnInit(): void {
    this.currentUser = this.authService.currentUser;
    const role = this.authService.getUserRole();
    this.canManagePayroll = ['HR', 'SUPER_ADMIN', 'CEO'].includes(role);

    if (this.canManagePayroll) {
      this.loadPayrollRecords();
    } else {
      this.activeTab = 'my-payslips';
      this.loadMyPayslips();
    }
  }

  setActiveTab(tab: string): void {
    this.activeTab = tab;

    if (tab === 'payroll' && this.canManagePayroll) {
      this.loadPayrollRecords();
    } else if (tab === 'overtime' && this.canManagePayroll) {
      this.loadPendingOvertimeApprovals();
    } else if (tab === 'deductions' && this.canManagePayroll) {
      this.loadDeductionTypes();
    } else if (tab === 'my-payslips') {
      this.loadMyPayslips();
    }
  }

  // Employee View Method
  loadMyPayslips(): void {
    if (!this.currentUser?.emp_id) return;

    this.loading = true;

    // Fetch Active Salary Structure
    this.salaryService.getActiveSalary(this.currentUser.emp_id).subscribe({
      next: (data) => {
        this.activeSalary = data;
      },
      error: (err) => {
        console.error('Error loading salary structure:', err);
      }
    });

    // Fetch Payslips
    this.payrollService.getEmployeePayrollHistory(this.currentUser.emp_id).subscribe({
      next: (data) => {
        this.myPayslips = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading payslips:', err);
        this.loading = false;
      }
    });
  }

  // Payroll Methods
  loadPayrollRecords(): void {
    if (!this.canManagePayroll) return;
    this.loading = true;
    this.payrollService.getPayrollList(this.selectedMonth, this.selectedYear).subscribe({
      next: (data) => {
        this.payrollRecords = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading payroll records:', err);
        this.loading = false;
      }
    });
  }

  processAllPayroll(): void {
    if (confirm(`Process payroll for all employees for ${this.getMonthName(this.selectedMonth)} ${this.selectedYear}?`)) {
      this.loading = true;
      this.payrollService.processAllPayroll(this.selectedMonth, this.selectedYear).subscribe({
        next: (result) => {
          alert(`Payroll processed for ${result.processed} employees`);
          this.loadPayrollRecords();
        },
        error: (err) => {
          console.error('Error processing payroll:', err);
          alert('Error processing payroll: ' + (err.error?.detail || 'Unknown error'));
          this.loading = false;
        }
      });
    }
  }

  processSinglePayroll(): void {
    if (!this.processSingleEmpId.trim()) {
      alert('Please enter an Employee ID');
      return;
    }

    this.loading = true;
    this.payrollService.processPayroll(this.processSingleEmpId.trim(), this.selectedMonth, this.selectedYear).subscribe({
      next: () => {
        alert(`Payroll processed for ${this.processSingleEmpId}`);
        this.processSingleEmpId = '';
        this.loadPayrollRecords();
      },
      error: (err) => {
        console.error('Error processing payroll:', err);
        alert('Error processing payroll: ' + (err.error?.detail || 'Unknown error'));
        this.loading = false;
      }
    });
  }

  downloadPayslip(payrollId: number, empId: string): void {
    this.payrollService.downloadPayslip(payrollId).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `Payslip_${empId}_${this.selectedMonth}_${this.selectedYear}.pdf`;
        link.click();
        window.URL.revokeObjectURL(url);
      },
      error: (err) => {
        console.error('Error downloading payslip:', err);
        alert('Error downloading payslip');
      }
    });
  }

  markAsPaid(payrollId: number, paymentMethod: string = 'Bank Transfer'): void {
    const paymentDate = new Date().toISOString().split('T')[0];
    this.payrollService.updatePaymentStatus(payrollId, 'PAID', paymentDate, paymentMethod).subscribe({
      next: () => {
        alert('Payment status updated to PAID via ' + paymentMethod);
        this.loadPayrollRecords();
      },
      error: (err) => {
        console.error('Error updating status:', err);
        alert('Error updating payment status');
      }
    });
  }

  // Salary Methods
  createSalaryStructure(): void {
    if (!this.salaryForm.emp_id || this.salaryForm.basic_salary <= 0) {
      alert('Please fill in all required fields');
      return;
    }

    this.salaryService.createSalaryStructure(this.salaryForm).subscribe({
      next: (result) => {
        alert('Salary structure created successfully');
        this.resetSalaryForm();
      },
      error: (err) => {
        console.error('Error creating salary:', err);
        alert('Error creating salary structure: ' + (err.error?.detail || 'Unknown error'));
      }
    });
  }

  resetSalaryForm(): void {
    this.salaryForm = {
      emp_id: '',
      basic_salary: 0,
      hra: 0,
      transport_allowance: 0,
      dearness_allowance: 0,
      medical_allowance: 0,
      special_allowance: 0,
      other_allowances: 0
    };
  }

  calculateGrossSalary(): number {
    return (Number(this.salaryForm.basic_salary) || 0) +
      (Number(this.salaryForm.hra) || 0) +
      (Number(this.salaryForm.transport_allowance) || 0) +
      (Number(this.salaryForm.dearness_allowance) || 0) +
      (Number(this.salaryForm.medical_allowance) || 0) +
      (Number(this.salaryForm.special_allowance) || 0) +
      (Number(this.salaryForm.other_allowances) || 0);
  }

  // Overtime Methods
  loadPendingOvertimeApprovals(): void {
    this.overtimeService.getPendingApprovals().subscribe({
      next: (data) => {
        this.pendingOvertimeApprovals = data;
      },
      error: (err) => {
        console.error('Error loading overtime approvals:', err);
      }
    });
  }

  approveOvertime(overtimeId: number): void {
    this.overtimeService.approveOvertime(overtimeId, 'APPROVE').subscribe({
      next: () => {
        alert('Overtime approved');
        this.loadPendingOvertimeApprovals();
      },
      error: (err) => {
        console.error('Error approving overtime:', err);
        alert('Error approving overtime');
      }
    });
  }

  rejectOvertime(overtimeId: number): void {
    const remarks = prompt('Enter rejection reason:');
    if (remarks) {
      this.overtimeService.approveOvertime(overtimeId, 'REJECT', remarks).subscribe({
        next: () => {
          alert('Overtime rejected');
          this.loadPendingOvertimeApprovals();
        },
        error: (err) => {
          console.error('Error rejecting overtime:', err);
          alert('Error rejecting overtime');
        }
      });
    }
  }

  // Deduction Methods
  loadDeductionTypes(): void {
    this.deductionService.getDeductionTypes().subscribe({
      next: (data) => this.deductionTypes = data,
      error: (err) => console.error('Error loading deduction types:', err)
    });
  }

  createDeductionType(): void {
    if (!this.newDeductionType.name) return;
    this.deductionService.createDeductionType(this.newDeductionType).subscribe({
      next: () => {
        alert('Deduction type created');
        this.loadDeductionTypes();
        this.newDeductionType = { name: '', description: '', calculation_type: 'FIXED', default_value: 0 };
      },
      error: (err) => alert('Error: ' + (err.error?.detail || 'Unknown error'))
    });
  }

  assignDeduction(): void {
    if (!this.deductionForm.emp_id || !this.deductionForm.deduction_type_id) {
      alert('Please fill employee ID and select deduction type');
      return;
    }
    this.deductionService.assignDeduction(this.deductionForm).subscribe({
      next: () => {
        alert('Deduction assigned successfully');
        this.loadEmployeeDeductions();
      },
      error: (err) => alert('Error: ' + (err.error?.detail || 'Unknown error'))
    });
  }

  loadEmployeeDeductions(): void {
    if (!this.deductionForm.emp_id) return;
    this.deductionService.getEmployeeDeductions(this.deductionForm.emp_id).subscribe({
      next: (data) => this.employeeDeductions = data,
      error: (err) => console.error('Error loading employee deductions:', err)
    });
  }

  deactivateDeduction(id: number): void {
    if (confirm('Deactivate this deduction?')) {
      this.deductionService.deactivateDeduction(id).subscribe({
        next: () => {
          alert('Deduction deactivated');
          this.loadEmployeeDeductions();
        },
        error: (err) => alert('Error deactivating deduction')
      });
    }
  }

  // Utility Methods
  getMonthName(month: number): string {
    const months = ['January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'];
    return months[month - 1] || '';
  }

  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  }
}
