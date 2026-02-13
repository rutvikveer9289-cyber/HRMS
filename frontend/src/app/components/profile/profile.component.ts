import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AttendanceService } from '../../services/attendance.service';
import { NotificationService } from '../../services/notification.service';
import { AuthService } from '../../services/auth.service';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css'
})
export class ProfileComponent implements OnInit {
  profile: any = {};
  loading = true;
  isAdmin = false;
  editing = false;
  editProfile: any = {};

  constructor(
    private attendanceService: AttendanceService,
    private notificationService: NotificationService,
    public authService: AuthService
  ) { }

  ngOnInit() {
    const role = this.authService.getUserRole();
    this.isAdmin = role === 'SUPER_ADMIN' || role === 'CEO';
    this.attendanceService.getProfile().subscribe({
      next: (res) => {
        this.profile = res;
        this.editProfile = { ...res };
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.notificationService.showAlert("Could not load profile.", "error");
      }
    });
  }

  toggleEdit() {
    this.editing = !this.editing;
    if (!this.editing) {
      this.editProfile = { ...this.profile };
    }
  }

  updateProfile() {
    this.attendanceService.updateProfile(this.editProfile).subscribe({
      next: () => {
        this.profile = { ...this.editProfile };
        this.editing = false;
        this.notificationService.showAlert("Profile updated successfully!", "success");
      },
      error: (err) => {
        this.notificationService.showAlert("Failed to update profile.", "error");
      }
    });
  }
}
