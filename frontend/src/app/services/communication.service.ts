import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Announcement {
    id: number;
    title: string;
    content: string;
    author_id: string;
    created_at: string;
}

export interface AppNotification {
    id: number;
    message: string;
    type: string;
    link?: string;
    is_read: boolean;
    created_at: string;
}

@Injectable({
    providedIn: 'root'
})
export class CommunicationService {
    private apiUrl = `${environment.apiUrl}/comms`;

    constructor(private http: HttpClient) { }

    // Announcements
    getAnnouncements(): Observable<Announcement[]> {
        return this.http.get<Announcement[]>(`${this.apiUrl}/announcements`);
    }

    postAnnouncement(data: { title: string, content: string }): Observable<any> {
        return this.http.post(`${this.apiUrl}/announcements`, data);
    }

    deleteAnnouncement(id: number): Observable<any> {
        return this.http.delete(`${this.apiUrl}/announcements/${id}`);
    }

    // Notifications
    getNotifications(): Observable<AppNotification[]> {
        return this.http.get<AppNotification[]>(`${this.apiUrl}/notifications`);
    }

    markRead(id: number): Observable<any> {
        return this.http.put(`${this.apiUrl}/notifications/${id}/read`, {});
    }

    markAllRead(): Observable<any> {
        return this.http.put(`${this.apiUrl}/notifications/read-all`, {});
    }

    deleteNotification(id: number): Observable<any> {
        return this.http.delete(`${this.apiUrl}/notifications/${id}`);
    }

    clearNotifications(): Observable<any> {
        return this.http.delete(`${this.apiUrl}/notifications/clear-all`);
    }
}
