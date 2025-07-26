import { Component, OnInit } from '@angular/core';
import { BackendService } from '../../services/backend.service';
import { NotificationService } from '../../services/notification.service';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { NavBarComponent } from '../nav-bar/nav-bar.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  providers: [BackendService],
  imports: [HttpClientModule, CommonModule, NavBarComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})

export class DashboardComponent implements OnInit {
  isFileUploaded: boolean = false;
  user_id = '';
  is_logged_in = false;
  dropdownOpen = false;
  hoveredFileId: number | null = null;
  files: any[] = [
  ]; // Placeholder data for file list

  // Push notifications Error display messages
  FILE_LOAD_ERROR_MESSAGE = "Failed to load user files!!"
  FILE_DELETE_ERROR_MESSAGE = "Failed to delete user file!!"
  FILE_UPLOAD_ERROR_MESSAGE = "Failed to upload!!"

  // Push notifications Success display messages
  FILE_UPLOAD_SUCCESS_MESSAGE = "Successfully Uploaded File!!"
  FILE_DELETE_SUCCESS_MESSAGE = "Successfully Deleted File!!"

  constructor(
    private service: BackendService,
    private notification: NotificationService,
    private http: HttpClient,
    private router: Router
  ) {}

  
  ngOnInit(): void {
    this.service.isLoggedIn().subscribe(
      (response: any) => {
        this.user_id = response.user_id || '';
        this.is_logged_in = true;
        console.log('User logged in:', this.user_id, this.is_logged_in);

        this.service.data$.subscribe((updatedData) => {
          console.log(updatedData);
          this.loadUserFiles();
        });
      },
      (error) => {
        console.error('Access denied:', error);
        this.is_logged_in = false;
        // redirect to auth page
        this.router.navigate(['/auth']);
        // show notification
        this.notification.showLoginAgainErrorNotification;
      }
    );
  }

  loadUserFiles(): void {
    this.service.getUserFiles(this.user_id).subscribe(
      (response: any) => {
        if (response && response.files) {
          this.files = response.files; // Assuming API returns a 'files' array
          console.log('Files loaded:', this.files);
        } else {
          console.warn('No files found for the user.');
        }
      },
      (error) => {
        console.error('Failed to load files:', error);
        this.notification.showErrorNotification(this.FILE_LOAD_ERROR_MESSAGE)
      }
    );
  }

  // Navigate to file operations page
  openFile(fileId: string): void {
    console.log('Navigating to file operations for file ID:', fileId);
    this.router.navigate(['/file', fileId]);
  }

  deleteFile(fileId: string, event: Event) {
    event.stopPropagation(); // Prevent click event on the file card
    console.log(fileId);

    this.service.deleteUserFile(fileId).subscribe(
      (response: any) => {
        console.log(response);
        if (response && response.msg == "success") {
          
          console.log('File deleted');
          this.files = this.files.filter((file) => file.file_id !== fileId);
          console.log(`File with ID ${fileId} deleted.`);
          this.notification.showSuccessNotification(this.FILE_DELETE_SUCCESS_MESSAGE);
        } else {
          console.warn('Error deleting: ', response.error);
          this.notification.showErrorNotification(this.FILE_DELETE_ERROR_MESSAGE);
        }
      },
      (error) => {
        console.error('Failed to delete:', error);
        this.notification.showErrorNotification(this.FILE_DELETE_ERROR_MESSAGE);
      }
    );
    
    
  }

  toggleDropdown(): void {
    this.dropdownOpen = !this.dropdownOpen;
    console.log('Dropdown state:', this.dropdownOpen);
  }


  async uploadFile(file:any) {
    if (!file) return;

    try {
      const response: any = await this.service.getPresignedUploadUrl(file.name).toPromise();
      const presignedUrl = response?.url;
      const file_id = response?.file_id;
      console.log(response);
      console.log(presignedUrl);
      console.log(file_id);
      if (presignedUrl) {
        await this.service.uploadFileToS3(file, presignedUrl).toPromise();
        console.log('File uploaded successfully');
        // after uploading to S3, call the backend api to upload new file to a user
        const file_data = {
          filename: file.name,
          file_id: file_id
        }
        const resp:any = await this.service.addFileToUser(file_data).toPromise();
        console.log("response", resp);
        this.service.updateData("files"); // can be any string
        // notification for successful file upload!!
        this.notification.showSuccessNotification(this.FILE_UPLOAD_SUCCESS_MESSAGE);
      } else {
        const error_msg = response?.error ? response?.error : this.FILE_UPLOAD_ERROR_MESSAGE;
        this.notification.showErrorNotification(error_msg);
      }
    } catch (error:any) {
      console.error('Error uploading file', error);
      const error_msg = error?.error.error ? `${error?.error.error}`: this.FILE_UPLOAD_ERROR_MESSAGE;
      this.notification.showErrorNotification(error_msg);
    }
  }

  async handleFileUpload(event: Event) {
    const input = event.target as HTMLInputElement;
  
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      console.log('File uploaded:', file.name);
      try {
        await this.uploadFile(file);
        this.isFileUploaded = true; // Set to true after successful upload
      } catch (error) {
        console.error('Error uploading file', error);
        this.isFileUploaded = false; // Ensure it remains false if an error occurs
      }
      // Make sure that you save file meta data in backend if uploaded successfully
    }
  }
  get showUploadGuide(): boolean {
    return this.files.length === 0;
  }
  
}
