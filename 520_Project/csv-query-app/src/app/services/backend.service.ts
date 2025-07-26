import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';

const Base_URL = "http://localhost:8000";

@Injectable({
  providedIn: 'root'
})
 

export class BackendService {
  private dataSubject = new BehaviorSubject<string>('Initial Value');
  private dataPythonSubject = new BehaviorSubject<string>('Initial Value');
  constructor(private http: HttpClient) {}

  // Method to login
  login(user_id: string, hashed_password: string) {
    
    const data = {
      "user_id": user_id,
      "hashed_password": hashed_password
    };
    return this.http.post(Base_URL+`/login`,data, { withCredentials: true });
  }

  // Method to register
  register(email: string, hashed_password: string) {
    const data = {
      "name": email,
      "email": email,
      "username": email,
      "hashed_password": hashed_password
    }
    return this.http.post(Base_URL+`/new_user`,data, { withCredentials: true });
  }

  isLoggedIn(){
    return this.http.get(Base_URL+`/auth_check`, { withCredentials: true });
  }
  // Method to logout

  logout() {
    return this.http.post(Base_URL+`/logout`,{}, { withCredentials: true });
  }

  // Method to request a pre-signed URL for uploading
  getPresignedUploadUrl(filename: string) {
    return this.http.get<{ url: string }>(Base_URL +`/api/user/generate-upload-url?filename=${filename}`);
  }

  // Method to request a pre-signed URL for downloading
  getPresignedDownloadUrl(file_id: string) {
    return this.http.get(Base_URL + `/api/user/generate-view-url?file_id=${file_id}`, { withCredentials: true });
  }

  // Method to upload file using the upload URL
  uploadFileToS3(file: File, presignedUrl: string) {
    const headers = { 'Content-Type': 'text/csv' };
    return this.http.put(presignedUrl, file, { headers });
  }

  // Method to add files to user file list
  addFileToUser(file_data: any) {
    console.log("called addFileToUser")
    const data = {
      'filename': file_data.filename,
      'file_id': file_data.file_id
    };
    return this.http.post(Base_URL +`/api/user/upload/file`, data, { withCredentials: true })
  }

  // Method to delete a user file using file_id
  deleteUserFile(file_id: any){
    const data = {
      'file_id': file_id
    };
    return this.http.post(Base_URL + `/api/user/delete/file`, data, {withCredentials: true});
  }

    // Method to ask query to the pandas llm
    getPandasQueryOutput(filekey: string, query: string, userid:string="default") {
      console.log("calling pandas llm agent...");
      const data = {
        "file_key": filekey,
        "query": query
      };
      return this.http.post(Base_URL+`/get-pandas-query`,data, { withCredentials: true });
    }

    // Method to ask query to the pandas llm
    getSqlQueryOutput(filekey: string, query: string, userid:string="default") {
      console.log("calling sql llm agent...");
      const data = {
        "file_key": filekey,
        "query": query
      };
      return this.http.post(Base_URL+`/get-sql-query`,data, { withCredentials: true });
    }

    getUserFiles(user_id: string)
    {
      const data = {
        "user_id": user_id
      };
      return this.http.post(Base_URL+`/api/user/all/files`,data, { withCredentials: true });
    }

  // Observable for components to subscribe to
  data$: Observable<string> = this.dataSubject.asObservable();

  // Update data
  updateData(newData: string): void {
    this.dataSubject.next(newData);
  }

  // Observable to display python code update
  dataPython$: Observable<string> = this.dataPythonSubject.asObservable();

  // Update data
  updateDataPython(newData: string): void {
    this.dataPythonSubject.next(newData);
  }

}
