import { Component, OnInit } from '@angular/core';
import { RouterModule, RouterOutlet, Router } from '@angular/router';
import { UploadComponent } from './components/upload/upload.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { CommonModule } from '@angular/common';
import { NotificationService, Alert } from './services/notification.service';
import { AttendanceService } from './services/attendance.service';
import { AuthService } from './services/auth.service';

import { CommunicationService, AppNotification } from './services/communication.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterModule, RouterOutlet, CommonModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {
  title = 'Employee Attendance Analytics';
  alerts: Alert[] = [];
  isAdmin = false;
  isHr = false;
  isCeo = false;
  hasDashboardData = false;
  profileMenuOpen = false;
  mainMenuOpen = false;
  sidebarOpen = false;
  notificationMenuOpen = false;
  notifications: AppNotification[] = [];
  unreadCount = 0;
  currentUser: any = null;

  constructor(
    public notificationService: NotificationService,
    public attendanceService: AttendanceService,
    public authService: AuthService,
    public commService: CommunicationService,
    public router: Router
  ) { }

  ngOnInit() {
    this.notificationService.alerts$.subscribe((alerts: Alert[]) => {
      this.alerts = alerts;
    });

    // Subscribe to current user for navigation and profile display
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      this.isAdmin = user?.role === 'SUPER_ADMIN' || user?.role === 'CEO';
      this.isHr = user?.role === 'HR' || user?.role === 'SUPER_ADMIN' || user?.role === 'CEO';
      this.isCeo = user?.role === 'CEO' || user?.role === 'SUPER_ADMIN';
    });

    // Subscribe to data availability
    this.attendanceService.hasData$.subscribe((available: boolean) => {
      this.hasDashboardData = available;
    });

    // Load notifications periodically
    if (this.authService.isLoggedIn()) {
      this.loadNotifications();
      setInterval(() => {
        // Only fetch in background if menu is closed to prevent flickering/UI reset
        if (this.authService.isLoggedIn() && !this.notificationMenuOpen) {
          this.loadNotifications();
        }
      }, 30000); // 30 seconds
    }
  }

  loadNotifications() {
    this.commService.getNotifications().subscribe({
      next: (data) => {
        this.notifications = data;
        this.unreadCount = data.filter(n => !n.is_read).length;
      }
    });
  }

  toggleNotificationMenu() {
    this.notificationMenuOpen = !this.notificationMenuOpen;
    if (this.notificationMenuOpen) {
      this.profileMenuOpen = false;
      this.sidebarOpen = false;
      // Mark all as read when opening to clear the badge
      if (this.unreadCount > 0) {
        this.markAllAsRead();
      }
    }
  }

  markAsRead(n: AppNotification) {
    if (!n.is_read) {
      // Optimistic
      n.is_read = true;
      this.unreadCount = Math.max(0, this.unreadCount - 1);

      this.commService.markRead(n.id).subscribe({
        error: () => this.loadNotifications() // Revert on error
      });
    }
    if (n.link) {
      this.router.navigate([n.link]);
      this.notificationMenuOpen = false;
    }
  }

  markAllAsRead() {
    // Only clear the badge count visually immediately
    this.unreadCount = 0;
    this.notifications.forEach(n => n.is_read = true);

    // Server Sync
    this.commService.markAllRead().subscribe({
      next: () => {
        // Note: We don't call loadNotifications() immediately here 
        // because the backend now only returns unread ones.
        // If we did, the list would vanish while the user is still looking at it.
        // Instead, the background interval or next manual open will handle the refresh.
      }
    });
  }

  deleteNotification(event: Event, n: AppNotification) {
    event.stopPropagation();
    // Optimistic
    this.notifications = this.notifications.filter(item => item.id !== n.id);
    if (!n.is_read) {
      this.unreadCount = Math.max(0, this.unreadCount - 1);
    }

    this.commService.deleteNotification(n.id).subscribe({
      error: () => this.loadNotifications()
    });
  }

  clearAllNotifications() {
    if (confirm('Are you sure you want to clear all notifications?')) {
      // Optimistic
      this.notifications = [];
      this.unreadCount = 0;

      this.commService.clearNotifications().subscribe({
        error: () => this.loadNotifications()
      });
    }
  }

  getInitials(user: any): string {
    const target = user || this.currentUser;
    if (!target) return '??';
    const name = target.full_name || target.email?.split('@')[0] || '';
    if (!name) return '??';
    const parts = name.split(/[. \-_]/).filter((p: string) => p.length > 0);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  }

  getUserDisplayName(user: any): string {
    const target = user || this.currentUser;
    if (!target) return 'User';
    return target.full_name || target.email?.split('@')[0] || 'User';
  }

  toggleProfileMenu() {
    this.profileMenuOpen = !this.profileMenuOpen;
    if (this.profileMenuOpen) {
      this.mainMenuOpen = false;
      this.sidebarOpen = false;
    }
  }

  toggleMainMenu() {
    this.mainMenuOpen = !this.mainMenuOpen;
    if (this.mainMenuOpen) this.profileMenuOpen = false;
  }

  toggleSidebar() {
    this.sidebarOpen = !this.sidebarOpen;
    if (this.sidebarOpen) {
      this.profileMenuOpen = false;
      this.mainMenuOpen = false;
    }
  }

  logout() {
    this.profileMenuOpen = false;
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  removeAlert(id: number) {
    this.notificationService.removeAlert(id);
  }
}
