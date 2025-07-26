import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { BackendService } from '../../services/backend.service';
import { NotificationService } from '../../services/notification.service';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import * as XLSX from 'xlsx'; // Import XLSX for parsing Excel/CSV files
import { Router, ActivatedRoute } from '@angular/router';
import { VoiceService } from '../../services/voice.service';
import { NavBarComponent } from '../nav-bar/nav-bar.component';
import * as Prism from 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-sql';   // Import SQL grammar



interface ChatMessage {
  text: string;
  isUser: boolean;
}

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss'],
  standalone: true,
  providers: [BackendService],
  imports: [CommonModule, FormsModule, ReactiveFormsModule, HttpClientModule, NavBarComponent],
})
export class FileUploadComponent implements OnInit {
  chatQuery = '';
  user_id = '';
  is_logged_in = false;
  isLoading: boolean = false; // To manage the reloading animation
  file_id: any;

  // New properties for header dropdown functionality
  dropdownOpen = false;

  // Add chatMessages property
  chatMessages: ChatMessage[] = [];

  // python code/ SQL query display variables
  pythonCode: string  = `Click Submit to show the corresponding Python code`;
  sqlQuery: string = `Click Submit to show the corresponding SQL Query`
  highlightedCode: string = '';

  // Push notifications Error display messages
  GENERATED_SUCCESS_MESSAGE = "Generated Results SuccessFully!!"
  COPY_SUCCESS_MESSAGE = "Successfully copied to clipboard!!"

  // Push notifications Success display messages
  GENERATED_FAILED_MESSAGE = "Failed to generate results!!"
  COPY_FAILED_MESSAGE = "Failed to copy to clipboard!!"

  constructor(
    private fb: FormBuilder,
    private service: BackendService,
    private notification: NotificationService,
    private router: Router,
    private route: ActivatedRoute,
    private speechRecognitionService: VoiceService,
    private http: HttpClient
  ) {
    this.fileForm = this.fb.group({
      file: [null],
    });
  }

  ngOnInit(): void {
    this.service.isLoggedIn().subscribe(
      (response: any) => {
        this.user_id = response.user_id;
        this.is_logged_in = true;
        console.log(this.user_id, this.is_logged_in);
        this.file_id = this.route.snapshot.paramMap.get('id');
        this.parseFileFromUrl();

        this.service.dataPython$.subscribe((updatedData) => {
          console.log(updatedData);
          if (this.queryType=="Pandas"){
            this.highlightedCode = Prism.highlight(this.pythonCode.trim().replace(/^\s*\n|\n\s*$/g, ''), Prism.languages['python'], 'python');
          }
          else {
            this.highlightedCode = Prism.highlight(this.sqlQuery.trim(), Prism.languages['sql'], 'sql');
          }
          
        })
      },
      (error) => {
        console.error('Access denied', error, this.is_logged_in);
        // redirect to auth page
        this.router.navigate(['/auth']);
        this.notification.showLoginAgainErrorNotification();
      }
    );

  }

  async onChatSubmit() {
    if (this.chatQuery.trim()) {
      // Add user message to chatMessages
      this.chatMessages.push({ text: this.chatQuery, isUser: true });

      // Simulate a bot response
      const botResponse = `Received your query: ${this.chatQuery}`;
      this.chatMessages.push({ text: botResponse, isUser: false });

      // Clear the chat input
      this.chatQuery = '';
    }
    this.query = this.chatQuery;
    await this.onSubmitQuery();
  }

  file: File | undefined;
  fileForm: FormGroup;
  fileData: any = null;
  queryResult: any = null;
  query = '';
  chatbotResponse = '';
  isResultTable = false;
  data: any[] = []; // To hold parsed table data
  headers: string[] = []; // To hold table headers

  // New properties for CSV Preview
  csvData: any[] = [];
  cols: string[] = [];


  async parseFileFromUrl() {
    const resp:any = await this.service.getPresignedDownloadUrl(this.file_id).toPromise();
    const url = resp?.url;
    console.log(url);
    this.http.get(url, { responseType: 'arraybuffer' }).subscribe({
      next: (fileData) => {
        const workbook = XLSX.read(fileData, { type: 'array' });
        const sheetName = workbook.SheetNames[0];
        const sheet = workbook.Sheets[sheetName];
        const jsonData = XLSX.utils.sheet_to_json<any[]>(sheet, { header: 1 });

        if (Array.isArray(jsonData)) {
          const maxRows = 50; // Limit rows to prevent rendering large files
          const maxCols = 50; // Limit columns to prevent rendering large files

          this.cols = jsonData[0]?.slice(0, maxCols) || [];
          this.csvData = jsonData.slice(1, maxRows).map((row: any[]) =>
            this.cols.reduce((acc: any, col: string, index: number) => {
              acc[col] = row[index] || '';
              return acc;
            }, {})
          );

          console.log('Columns:', this.cols);
          console.log('CSV Data:', this.csvData);
        } else {
          console.error('Invalid data format');
        }
      },
      error: (err) => {
        console.error('Error fetching file:', err);
      },
    });
  }


  async onSubmitQuery() {
    console.log("called onSubmitQuery");
    if (this.query) {
      console.log('Query submitted:', this.query);
      this.isLoading = true; // Start reloading animation
  
      try {
        if (true) {
          if (this.queryType == "Pandas") {
            this.service.getPandasQueryOutput(this.file_id, this.query, 'default').subscribe({
              next: (response: any) => {
                console.log(response);
                const result = JSON.parse(response['result']);
                this.queryResult = response['query'];
                this.pythonCode = this.queryResult;
                this.service.updateDataPython("python");
                this.headers = Object.keys(result);
                this.isResultTable = response['is_table'];
  
                const rows = Object.keys(result[this.headers[0]]);
                this.data = rows.map((rowId) => {
                  let row: any = {};
                  this.headers.forEach((header) => {
                    row[header] = result[header][rowId];
                  });
                  return row;
                });
                this.notification.showSuccessNotification(this.GENERATED_SUCCESS_MESSAGE);
                this.isLoading = false; // Stop reloading animation
              },
              error: (error: any) => {
                console.error('Error sending the query', error);
                const error_msg = error?.error.error ? `${error?.error.error}`: this.GENERATED_FAILED_MESSAGE;
                this.notification.showErrorNotification(error_msg);
                this.isLoading = false; // Stop reloading animation on error
              },
            });
          } else {
            this.service.getSqlQueryOutput(this.file_id, this.query, 'default').subscribe({
              next: (response: any) => {
                console.log(response);
                const result = JSON.parse(response['result']);
                this.queryResult = response['query'];
                this.sqlQuery = this.queryResult;
                this.service.updateDataPython("sql");
                this.headers = Object.keys(result);
                this.isResultTable = response['is_table'];
  
                const rows = Object.keys(result[this.headers[0]]);
                this.data = rows.map((rowId) => {
                  let row: any = {};
                  this.headers.forEach((header) => {
                    row[header] = result[header][rowId];
                  });
                  return row;
                });
                this.notification.showSuccessNotification(this.GENERATED_SUCCESS_MESSAGE);
                this.isLoading = false; // Stop reloading animation
              },
              error: (error) => {
                console.error('Error sending the query', error);
                const error_msg = error?.error.error ? `${error?.error.error}`: this.GENERATED_FAILED_MESSAGE;
                this.notification.showErrorNotification(error_msg);
                this.isLoading = false; // Stop reloading animation on error
              },
            });
          }
        } else {
          console.log('No file found!!');
          this.isLoading = false; // Stop reloading animation if no file is found
        }
      } catch (error) {
        console.error('Unexpected error in query submission', error);
        this.notification.showErrorNotification(this.GENERATED_FAILED_MESSAGE);
        this.isLoading = false; // Stop reloading animation on exception
      }
    }
  }
  
  
  // Function to download data as CSV
  downloadCsv() {
    const headers = this.headers.join(',');  // Join headers as the first row in the CSV
    const rows = this.data.map((row: any) =>
      this.headers.map((header: string) => row[header]).join(',')
    );  // Join the data for each row
  
    // Combine headers and rows into a single string
    const csvContent = [headers, ...rows].join('\n');
  
    // Create a Blob with the CSV content and trigger the download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'query_results.csv');
    link.click();
    URL.revokeObjectURL(url);
  }
  

  
  toggleDropdown() {
    this.dropdownOpen = !this.dropdownOpen;
  }


  queryType: string = 'Pandas'; // Default to 'Pandas'

  startVoiceInput(): void {
    if (!this.speechRecognitionService.isListening) {
      this.speechRecognitionService.startListening((text: string) => {
        this.query += ` ${text}`;
      });
    }
  }

  stopVoiceInput(): void {
    this.speechRecognitionService.stopListening();
  }

  copyCode(): void {
    navigator.clipboard.writeText(this.pythonCode).then(() => {
      this.notification.showSuccessNotification(this.COPY_SUCCESS_MESSAGE);
    }).catch(err => {
      console.error('Could not copy text: ', err);
      this.notification.showErrorNotification(this.COPY_FAILED_MESSAGE);
    });
  }

  onQueryTypeChange(selectedType: string): void {
    console.log('Query Type changed to:', selectedType);
    this.service.updateDataPython(selectedType);
    // Add additional logic here as needed
  }

}
