import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PayrollService } from '../../services/payroll.service';
import { SalaryService } from '../../services/salary.service';

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
  showSummary: boolean = true;
  activeStat: string | null = null; // Track which specific stat is expanded

  toggleStat(stat: string): void {
    this.activeStat = this.activeStat === stat ? null : stat;
  }

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
  isAllHistory: boolean = false;
  processSingleEmpId: string = '';
  ledgerSearch: string = '';
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


  // Payment tracking
  paymentFilter: string = 'all'; // 'all', 'paid', 'pending'

  // Edit Modal State
  isEditModalOpen: boolean = false;
  editingRecord: any = null;

  constructor(
    private payrollService: PayrollService,
    private salaryService: SalaryService,
    // OvertimeService removed
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

  // Payment Summary Methods
  getPaidCount(): number {
    return this.payrollRecords.filter(r => r.status === 'PAID').length;
  }

  getPendingCount(): number {
    return this.payrollRecords.filter(r => r.status !== 'PAID').length;
  }

  getTotalPaidAmount(): number {
    return this.payrollRecords
      .filter(r => r.status === 'PAID')
      .reduce((sum, r) => sum + (r.net_salary || 0), 0);
  }

  getTotalPendingAmount(): number {
    return this.payrollRecords
      .filter(r => r.status !== 'PAID')
      .reduce((sum, r) => sum + (r.net_salary || 0), 0);
  }

  getTotalPayrollAmount(): number {
    return this.payrollRecords.reduce((sum, r) => sum + (r.net_salary || 0), 0);
  }

  // Filter Methods
  getFilteredRecords(): any[] {
    let records = this.payrollRecords;

    if (this.isAllHistory) {
      // In Ledger view, only show PAID records as requested
      records = records.filter(r => r.status === 'PAID');

      if (this.ledgerSearch) {
        const search = this.ledgerSearch.toLowerCase();
        records = records.filter(r => {
          const empName = (r.owner?.full_name || '').toLowerCase();
          const empId = (r.emp_id || '').toLowerCase();
          const month = this.getMonthName(r.month || 0).toLowerCase();
          const year = (r.year || '').toString();
          return empName.includes(search) ||
            empId.includes(search) ||
            month.includes(search) ||
            year.includes(search);
        });
      }
      return records;
    }

    if (this.paymentFilter === 'paid') {
      return records.filter(r => r.status === 'PAID');
    } else if (this.paymentFilter === 'pending') {
      return records.filter(r => r.status !== 'PAID');
    }
    return records;
  }

  // Bulk Selection Methods
  toggleSelectAll(event: any): void {
    const checked = event.target.checked;
    this.payrollRecords.forEach(record => {
      if (record.status !== 'PAID') {
        record.selected = checked;
      }
    });
  }

  isAllSelected(): boolean {
    const unpaidRecords = this.payrollRecords.filter(r => r.status !== 'PAID');
    return unpaidRecords.length > 0 && unpaidRecords.every(r => r.selected);
  }

  getSelectedCount(): number {
    return this.payrollRecords.filter(r => r.selected).length;
  }

  clearSelection(): void {
    this.payrollRecords.forEach(r => r.selected = false);
  }

  bulkMarkAsPaid(paymentMethod: string): void {
    const selectedRecords = this.payrollRecords.filter(r => r.selected && r.status !== 'PAID');

    if (selectedRecords.length === 0) {
      alert('No records selected');
      return;
    }

    // Check if Razorpay payment possible
    const useRazorpay = ['Bank Transfer', 'IMPS', 'NEFT', 'RTGS'].includes(paymentMethod)
      && confirm(`Do you want to initiate REAL PAYMENT for ${selectedRecords.length} employees via Razorpay?\n\nClick OK for Real Payment (Money will be transferred)\nClick Cancel for Manual Tracking only`);

    if (useRazorpay) {
      // Real Payment via Razorpay
      const payrollIds = selectedRecords.map(r => r.id);
      const mode = 'IMPS'; // Default or derive from paymentMethod

      this.loading = true;
      this.payrollService.initiateBulkPayment(payrollIds, mode).subscribe({
        next: (result) => {
          alert(`Razorpay Payment Initiated!\nSuccessful: ${result.successful}\nFailed: ${result.failed}\nMessage: ${result.message}`);
          this.loadPayrollRecords();
          this.clearSelection();
          this.loading = false;
        },
        error: (err) => {
          console.error('Razorpay Error:', err);
          alert('Razorpay Payment Failed: ' + (err.error?.detail || err.message));
          this.loading = false;
        }
      });
    } else {
      // Manual Tracking (Old Way)
      if (confirm(`Mark ${selectedRecords.length} employees as manually PAID via ${paymentMethod}?`)) {
        const paymentDate = new Date().toISOString().split('T')[0];
        let completed = 0;

        selectedRecords.forEach(record => {
          this.payrollService.updatePaymentStatus(record.id, 'PAID', paymentDate, paymentMethod).subscribe({
            next: () => {
              completed++;
              if (completed === selectedRecords.length) {
                alert(`Successfully marked ${completed} payments as PAID (Manual)`);
                this.loadPayrollRecords();
                this.clearSelection();
              }
            },
            error: (err) => {
              console.error('Error updating payment:', err);
            }
          });
        });
      }
    }
  }

  // Edit Payroll Logic
  editPayroll(record: any): void {
    // Clone record to avoid direct mutation affecting the listview before save
    this.editingRecord = { ...record };
    this.isEditModalOpen = true;
  }

  closeEditModal(): void {
    this.isEditModalOpen = false;
    this.editingRecord = null;
  }

  savePayrollChanges(): void {
    if (!this.editingRecord) return;

    // Sanitize numeric fields to ensure keys are present and 0 is sent instead of null
    const numericFields = [
      'basic_salary', 'hra', 'transport_allowance', 'dearness_allowance',
      'medical_allowance', 'special_allowance', 'other_allowances',
      'total_deductions'
    ];

    numericFields.forEach(key => {
      // Use Number() to handle strings, and fallback to 0 if NaN/null/undefined
      this.editingRecord[key] = Number(this.editingRecord[key]) || 0;
    });

    this.loading = true;
    this.payrollService.updatePayrollDetails(this.editingRecord.id, this.editingRecord).subscribe({
      next: (updatedRecord) => {
        alert('Payroll record updated successfully');
        this.closeEditModal();
        this.loadPayrollRecords(); // Reload to reflect changes
      },
      error: (err) => {
        console.error('Error updating payroll:', err);
        alert('Error updating payroll: ' + (err.error?.detail || err.message));
        this.loading = false;
      }
    });
  }

  // Payment Modal Logic
  isPaymentModalOpen: boolean = false;
  paymentRecord: any = null;
  paymentDetails: any = {
    method: 'Bank Transfer',
    date: new Date().toISOString().split('T')[0],
    reference: '',
    note: '',
    isRealPayment: false,
    transferMode: 'IMPS'
  };

  openPaymentModal(record: any): void {
    this.paymentRecord = record;
    this.paymentDetails = {
      method: 'Bank Transfer',
      date: new Date().toISOString().split('T')[0],
      reference: '',
      note: '',
      isRealPayment: false,
      transferMode: 'IMPS'
    };
    this.isPaymentModalOpen = true;
  }

  closePaymentModal(): void {
    this.isPaymentModalOpen = false;
    this.paymentRecord = null;
  }

  confirmDisbursement(): void {
    if (!this.paymentRecord) return;

    if (this.paymentDetails.isRealPayment) {
      if (!confirm(`CONFIRM REAL PAYMENT: Transfer ₹${this.paymentRecord.net_salary} to ${this.paymentRecord.emp_id}? This action cannot be reversed.`)) return;

      this.loading = true;
      this.payrollService.initiateSinglePayment(this.paymentRecord.id, this.paymentDetails.transferMode).subscribe({
        next: (result) => {
          alert(`Razorpay Payment Successful!\nTransaction ID: ${result.transaction_id}\nUTR: ${result.utr || 'Pending'}`);
          this.closePaymentModal();
          this.loadPayrollRecords();
        },
        error: (err) => {
          console.error('Razorpay Error:', err);
          alert('Razorpay Payment Failed: ' + (err.error?.detail || err.message));
          this.loading = false;
        }
      });
      return;
    }

    if (!this.paymentDetails.reference && this.paymentDetails.method !== 'Cash') {
      if (!confirm('Proceed without Transaction Reference?')) return;
    }

    this.loading = true;
    this.payrollService.updatePaymentStatus(
      this.paymentRecord.id,
      'PAID',
      this.paymentDetails.date,
      this.paymentDetails.method,
      this.paymentDetails.reference, // mapping reference to transaction_id
      this.paymentDetails.reference  // mapping reference to UTR as well for completeness
    ).subscribe({
      next: () => {
        alert('Payment Recorded Successfully');
        this.closePaymentModal();
        this.loadPayrollRecords();
      },
      error: (err) => {
        console.error(err);
        alert('Payment Failed: ' + (err.error?.detail || err.message));
        this.loading = false;
      }
    });
  }

  setActiveTab(tab: string): void {
    this.activeTab = tab;

    if (tab === 'payroll' && this.canManagePayroll) {
      this.loadPayrollRecords();
    } else if (tab === 'history' && this.canManagePayroll) {
      this.loadAllHistory();
    } else if (tab === 'overtime' && this.canManagePayroll) {
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
    this.isAllHistory = false;
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

  loadAllHistory(): void {
    if (!this.canManagePayroll) return;

    if (this.isAllHistory) {
      // If already viewing history, toggle back to current month
      this.isAllHistory = false;
      this.loadPayrollRecords();
      return;
    }

    this.isAllHistory = true;
    this.loading = true;
    this.payrollService.getAllPayroll().subscribe({
      next: (data) => {
        this.payrollRecords = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading master history:', err);
        alert('Error loading master history');
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

  deletePayrollRecord(id: number): void {
    if (!confirm('Are you sure you want to delete this payroll record? This will revert the processing status for this employee for the month.')) {
      return;
    }

    this.loading = true;
    this.payrollService.deletePayrollRecord(id).subscribe({
      next: () => {
        alert('Payroll record deleted successfully');
        this.loadPayrollRecords();
      },
      error: (err) => {
        console.error('Error deleting payroll:', err);
        alert('Error deleting payroll: ' + (err.error?.detail || err.message));
        this.loading = false;
      }
    });
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
    const useRazorpay = ['Bank Transfer', 'IMPS', 'NEFT', 'RTGS'].includes(paymentMethod)
      && confirm('Do you want to initiate REAL PAYMENT via Razorpay?\n\nClick OK for Real Payment\nClick Cancel for Manual Tracking');

    if (useRazorpay) {
      this.loading = true;
      this.payrollService.initiateSinglePayment(payrollId, 'IMPS').subscribe({
        next: (result) => {
          alert(`Razorpay Payment Successful!\nTransaction ID: ${result.transaction_id}`);
          this.loadPayrollRecords();
          this.loading = false;
        },
        error: (err) => {
          console.error('Razorpay Error:', err);
          alert('Razorpay Payment Failed: ' + (err.error?.detail || err.message));
          this.loading = false;
        }
      });
    } else {
      // Manual Tracking
      const paymentDate = new Date().toISOString().split('T')[0];
      this.payrollService.updatePaymentStatus(payrollId, 'PAID', paymentDate, paymentMethod).subscribe({
        next: () => {
          alert('Payment status updated to PAID via ' + paymentMethod + ' (Manual)');
          this.loadPayrollRecords();
        },
        error: (err) => {
          console.error('Error updating status:', err);
          alert('Error updating payment status');
        }
      });
    }
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
