import { Component, OnInit } from '@angular/core';
import { BackendService } from '../../services/backend.service';
import { NotificationService } from '../../services/notification.service';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-nav-bar',
  standalone: true,
  imports: [],
  templateUrl: './nav-bar.component.html',
  styleUrl: './nav-bar.component.scss'
})
export class NavBarComponent implements OnInit{
  constructor(
    private service: BackendService,
    private notification: NotificationService,
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit(): void {
    
  }
  logout(): void {
    
    this.service.logout().subscribe(
      (response: any) => {
        if (response && response.msg == "Logout successful") {
          
          console.log('Logged out...');
          // this.is_logged_in = false;
          this.router.navigate(['/auth']);
          this.notification.showLogOutSuccessNotification();
        } else {
          console.warn('Error logging out');
        }
      },
      (error) => {
        console.error('Failed to logout:', error);
      }
    );
    
    
  }


}
