import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
    providedIn: 'root'
})
export class DeductionService {
    private apiUrl = `${environment.apiUrl}/deductions`;

    constructor(private http: HttpClient) { }

    getDeductionTypes(): Observable<any[]> {
        return this.http.get<any[]>(`${this.apiUrl}/types`);
    }

    createDeductionType(data: any): Observable<any> {
        return this.http.post(`${this.apiUrl}/types`, data);
    }

    assignDeduction(data: any): Observable<any> {
        return this.http.post(`${this.apiUrl}/assign`, data);
    }

    getEmployeeDeductions(empId: string): Observable<any[]> {
        return this.http.get<any[]>(`${this.apiUrl}/employee/${empId}`);
    }

    deactivateDeduction(deductionId: number): Observable<any> {
        return this.http.delete(`${this.apiUrl}/${deductionId}`);
    }
}
