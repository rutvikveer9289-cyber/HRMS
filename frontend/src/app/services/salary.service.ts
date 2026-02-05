import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
    providedIn: 'root'
})
export class SalaryService {
    private apiUrl = `${environment.apiUrl}/salary`;

    constructor(private http: HttpClient) { }

    createSalaryStructure(salaryData: any): Observable<any> {
        return this.http.post(`${this.apiUrl}/structure`, salaryData);
    }

    getActiveSalary(empId: string): Observable<any> {
        return this.http.get(`${this.apiUrl}/structure/${empId}`);
    }

    getSalaryHistory(empId: string): Observable<any[]> {
        return this.http.get<any[]>(`${this.apiUrl}/history/${empId}`);
    }

    updateSalaryStructure(salaryId: number, salaryData: any): Observable<any> {
        return this.http.put(`${this.apiUrl}/structure/${salaryId}`, salaryData);
    }
}
