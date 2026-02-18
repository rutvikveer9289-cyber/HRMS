import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ParticleBgComponent } from '../particle-bg/particle-bg.component';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, ParticleBgComponent],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  loginData = {
    email: '',
    password: ''
  };

  showPassword = false;
  showNewPassword = false;

  // Forgot Password Flow
  showForgotPasswordModal = false;
  forgotPasswordStep: 'email' | 'otp' | 'success' = 'email';
  forgotEmail = '';
  resetOtp = '';
  newPassword = '';
  confirmNewPassword = '';

  error = '';
  loading = false;

  constructor(private authService: AuthService, private router: Router) { }

  onLogin() {
    this.error = '';
    this.loading = true;
    this.authService.login(this.loginData).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.loading = false;
        this.error = this.formatError(err);
      }
    });
  }

  openForgotPassword() {
    this.showForgotPasswordModal = true;
    this.forgotPasswordStep = 'email';
    this.forgotEmail = '';
    this.resetOtp = '';
    this.newPassword = '';
    this.confirmNewPassword = '';
    this.error = '';
  }

  closeForgotPassword() {
    this.showForgotPasswordModal = false;
    this.error = '';
  }

  sendResetOtp() {
    this.error = '';
    this.loading = true;
    this.authService.forgotPassword(this.forgotEmail).subscribe({
      next: (res) => {
        this.loading = false;
        this.forgotPasswordStep = 'otp';
        alert(res.message || 'OTP sent to your email');
      },
      error: (err) => {
        this.loading = false;
        this.error = this.formatError(err);
      }
    });
  }

  resetPassword() {
    this.error = '';

    if (this.newPassword !== this.confirmNewPassword) {
      this.error = 'Passwords do not match';
      return;
    }

    if (this.newPassword.length < 8) {
      this.error = 'Password must be at least 8 characters';
      return;
    }

    this.loading = true;
    this.authService.resetPassword(this.forgotEmail, this.resetOtp, this.newPassword).subscribe({
      next: (res) => {
        this.loading = false;
        this.forgotPasswordStep = 'success';
        setTimeout(() => {
          this.closeForgotPassword();
        }, 2000);
      },
      error: (err) => {
        this.loading = false;
        this.error = this.formatError(err);
      }
    });
  }

  private formatError(err: any): string {
    console.error('Auth error:', err);
    const detail = err.error?.detail;
    if (typeof detail === 'string') {
      return detail;
    } else if (Array.isArray(detail)) {
      return detail.map(d => d.msg || d.message || JSON.stringify(d)).join(', ');
    } else if (detail && typeof detail === 'object') {
      return detail.msg || detail.message || JSON.stringify(detail);
    }
    return err.error?.message || err.message || 'An unexpected error occurred';
  }
}
