import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  // Common Push notifications Error display messages
  ACCESS_DENIED_LOGIN_AGAIN_MESSAGE = "Access Denied!! Please Login!!"

  // Common Push notifications Success display messages
  USER_LOGOUT_SUCCESS_MESSAGE = "Successfully Logged out User!!"
  constructor(private snackBar: MatSnackBar) {}

  showNotification(message: string, action: string = 'Close', duration: number = 5000, pClass: string = 'error-snackbar'): void {
    this.snackBar.open(message, action, {
      duration: duration,
      horizontalPosition: 'center',
      verticalPosition: 'bottom',
      panelClass: pClass
    });
  }

  showErrorNotification(message: string, duration: number = 5000, action='Close') {
    this.showNotification(message, action, duration, 'error-snackbar');
  }

  showSuccessNotification(message: string, duration: number = 5000, action='Close') {
    this.showNotification(message, action, duration, 'success-snackbar');
  }

  showLoginAgainErrorNotification() {
    this.showErrorNotification(this.ACCESS_DENIED_LOGIN_AGAIN_MESSAGE);
  }

  showLogOutSuccessNotification() {
    this.showSuccessNotification(this.USER_LOGOUT_SUCCESS_MESSAGE);
  }

}
