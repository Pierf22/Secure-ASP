import { Component, inject, OnInit } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { AlertService } from '../../services/alert/alert.service';
import { CertificationRequestService } from '../../services/certification-request/certification-request.service';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { NgClass, NgForOf, NgIf } from '@angular/common';
import { AuthService } from '../../services/auth/auth.service';
import { CertificationRequestSave } from '../../models/certification-request';

@Component({
  selector: 'app-new-certification-modal',
  standalone: true,
  imports: [  
    NgIf,
    NgClass,
    ReactiveFormsModule,
    NgForOf],
  templateUrl: './new-certification-modal.component.html',
  styleUrl: './new-certification-modal.component.css'
})
export class NewCertificationModalComponent implements OnInit {
  constructor(private alert:AlertService, private certificationService:CertificationRequestService, private fb:FormBuilder, private authService:AuthService) {
    this.form = this.fb.group({
      document_type: ['', Validators.required],
      document_front: [null, Validators.required],
      document_back: [null, Validators.required],
    });
   }
  modal = inject(NgbActiveModal);
  protected documentTypes:string[] = [];
  protected form:FormGroup;



  ngOnInit(): void {
    this.alert.showSpinner();
    this.certificationService.getDocumentTypes().subscribe(
      data => {
        this.documentTypes = data;
        this.alert.hideSpinner();

      },
      error => {
        if(error.status===401 || error.status===403){
          this.modal.close();
        }
        this.alert.error("Error getting document types, please try again later");

      }
    );
  }
  deSelectDocumentType() {
    this.form.patchValue({document_type: ''});
  }
  saveDocumentType(document: string) {
    this.form.patchValue({document_type: document});
   
  }
  onDocumentTypeChange(event: Event) {
    const selectedValue = (event.target as HTMLSelectElement).value;
    
    if (selectedValue === "") {
      this.deSelectDocumentType(); // Se l'utente seleziona l'opzione predefinita
    } else {
      this.saveDocumentType(selectedValue); // Salva il tipo di documento selezionato
    }
  }
  
  uploadFrontFile($event: Event) {
  
    let file = ($event.target as HTMLInputElement).files?.item(0);
    const max_size = 10 * 1024 * 1024;
    if(file){
      if(file.size>max_size){
        this.form.get('document_front')?.setErrors({'max_size': true});
        return;
      }else {
        this.form.get('document_front')?.setErrors(null);
        // @ts-ignore
        this.form.patchValue({document_front: file});
      }
    }

  }

  uploadBackFile($event: Event) {
    let file = ($event.target as HTMLInputElement).files?.item(0);
    const max_size = 10 * 1024 * 1024;
    if(file){
      if(file.size>max_size){
        this.form.get('document_back')?.setErrors({'max_size': true});
        return;
      }else {
        this.form.get('document_back')?.setErrors(null);
        // @ts-ignore
        this.form.patchValue({document_back: file});
   
      
      }
    }
  }

  protected saveCertificationRequest() {
    this.alert.showSpinner();
    const userId = this.authService.getUserId();
    if(!userId)
      return;
    const document_type = this.form.get('document_type')?.value;
    const document_front = this.form.get('document_front')?.value;
    const document_back = this.form.get('document_back')?.value;
    if(!document_type || !document_front || !document_back){
      this.alert.error("Please fill all the fields");
      return;
    }
    const certification:CertificationRequestSave = new CertificationRequestSave(document_front, document_back, document_type);
    this.certificationService.saveCertificationRequest(userId, certification).subscribe(
      data => {
        this.alert.hideSpinner();
        this.modal.close();
      },
      error => {
        this.alert.hideSpinner();
        if(error.status===401){
          this.alert.warning("Please login to save a certification request");
          this.modal.close();
          return;
        }
        this.alert.error("Error saving certification request, please try again later");
  });
}



}
