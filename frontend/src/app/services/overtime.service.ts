import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
    providedIn: 'root'
})
export class OvertimeService {
    private apiUrl = `${environment.apiUrl}/overtime`;

    constructor(private http: HttpClient) { }

    calculateOvertime(empId: string, startDate: string, endDate: string, overtimeRate: number = 1.5): Observable<any[]> {
        return this.http.post<any[]>(`${this.apiUrl}/calculate`, {
            emp_id: empId,
            start_date: startDate,
            end_date: endDate,
            overtime_rate: overtimeRate
        });
    }

    getEmployeeOvertime(empId: string): Observable<any[]> {
        return this.http.get<any[]>(`${this.apiUrl}/${empId}`);
    }

    getPendingApprovals(): Observable<any[]> {
        return this.http.get<any[]>(`${this.apiUrl}/pending/approvals`);
    }

    approveOvertime(overtimeId: number, action: string, remarks?: string): Observable<any> {
        return this.http.put(`${this.apiUrl}/approve`, {
            overtime_id: overtimeId,
            action,
            remarks
        });
    }

    getOvertimeSummary(empId: string, month: number, year: number): Observable<any> {
        return this.http.get(`${this.apiUrl}/summary/${empId}/${month}/${year}`);
    }

    getTopEarners(month: number, year: number, limit: number = 5): Observable<any[]> {
        return this.http.get<any[]>(`${this.apiUrl}/analytics/top-earners`, {
            params: { month: month.toString(), year: year.toString(), limit: limit.toString() }
        });
    }
}
