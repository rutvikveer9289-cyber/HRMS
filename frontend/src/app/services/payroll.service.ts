import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
    providedIn: 'root'
})
export class PayrollService {
    private apiUrl = `${environment.apiUrl}/payroll`;

    constructor(private http: HttpClient) { }

    processPayroll(empId: string, month: number, year: number): Observable<any> {
        return this.http.post(`${this.apiUrl}/process`, { emp_id: empId, month, year });
    }

    processAllPayroll(month: number, year: number): Observable<any> {
        return this.http.post(`${this.apiUrl}/process-all/${month}/${year}`, {});
    }

    getPayrollRecord(empId: string, month: number, year: number): Observable<any> {
        return this.http.get(`${this.apiUrl}/${empId}/${month}/${year}`);
    }

    getPayrollList(month: number, year: number): Observable<any[]> {
        return this.http.get<any[]>(`${this.apiUrl}/list/${month}/${year}?t=${new Date().getTime()}`);
    }

    getAllPayroll(): Observable<any[]> {
        return this.http.get<any[]>(`${this.apiUrl}/all`);
    }

    downloadPayslip(payrollId: number): Observable<Blob> {
        return this.http.get(`${this.apiUrl}/download/${payrollId}`, { responseType: 'blob' });
    }

    updatePaymentStatus(payrollId: number, status: string, paymentDate?: string, paymentMethod?: string, transactionId?: string, utrNumber?: string): Observable<any> {
        return this.http.put(`${this.apiUrl}/status/${payrollId}`, {
            status,
            payment_date: paymentDate,
            payment_method: paymentMethod,
            transaction_id: transactionId,
            utr_number: utrNumber
        });
    }

    updatePayrollDetails(payrollId: number, data: any): Observable<any> {
        return this.http.put(`${this.apiUrl}/${payrollId}`, data);
    }

    getEmployeePayrollHistory(empId: string, limit: number = 12): Observable<any[]> {
        return this.http.get<any[]>(`${this.apiUrl}/employee/${empId}?limit=${limit}`);
    }

    // Razorpay Methods
    initiateSinglePayment(payrollId: number, mode: string = 'IMPS'): Observable<any> {
        return this.http.post(`${environment.apiUrl}/razorpay/payout/single`, {
            payroll_id: payrollId,
            mode: mode
        });
    }

    initiateBulkPayment(payrollIds: number[], mode: string = 'IMPS'): Observable<any> {
        return this.http.post(`${environment.apiUrl}/razorpay/payout/bulk`, {
            payroll_ids: payrollIds,
            mode: mode
        });
    }

    deletePayrollRecord(payrollId: number): Observable<any> {
        return this.http.delete(`${this.apiUrl}/${payrollId}`);
    }
}
