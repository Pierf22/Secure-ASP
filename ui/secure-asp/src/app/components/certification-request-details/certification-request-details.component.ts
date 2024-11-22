import { NgClass, NgIf } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { CertificationRequest } from '../../models/certification-request';
import { AlertService } from '../../services/alert/alert.service';
import { AuthService } from '../../services/auth/auth.service';
import { CertificationRequestService } from '../../services/certification-request/certification-request.service';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { NewCertificationModalComponent } from '../new-certification-modal/new-certification-modal.component';

@Component({
  selector: 'app-certification-request-details',
  standalone: true,
  imports: [NgIf, NgClass],
  templateUrl: './certification-request-details.component.html',
  styleUrl: './certification-request-details.component.css'
})
export class CertificationRequestDetailsComponent implements OnInit{
  constructor(private alert:AlertService, private authService:AuthService, private certificationService:CertificationRequestService) {}
  ngOnInit(): void {
    this.alert.showSpinner();
    const userId = this.authService.getUserId();
    if(!userId)
      return
    this.certificationService.getCertificationRequest(userId).subscribe(
      data => {

        this.certificationRequest= data;
        this.alert.hideSpinner();

      },
      error => {
        this.alert.hideSpinner();
        if(error.status===401){
          return;
        }
        if(error.status===404){
          this.certificationRequest=undefined;
          this.alert.hideSpinner();
          return;
        }
        this.alert.error("Error getting certification request, please try again later");
      }
    );
  }
  certificationRequest: CertificationRequest | undefined;
  private modalService = inject(NgbModal);



  hasACertification() {
    return this.certificationRequest!==undefined;
  }

  openNewCertificationModal() {

    this.modalService.open(NewCertificationModalComponent, { ariaLabelledBy: 'modal-new-certification' }).result.then(
      (result) => {
        this.alert.success("Certification request submitted successfully");
        this.ngOnInit();

      },
      (reason) => {

      });
  

  }





  deleteCertification() {
    this.alert.showSpinner();
    const certificationId = this.certificationRequest?.id;
    if(!certificationId)
      return;
    this.certificationService.deleteCertificationRequest(certificationId).subscribe(
      data => {
        this.alert.success("Certification request deleted successfully").then(() => {
          this.ngOnInit();
        });
      },
      error => {
        if(error.status===401){
          this.alert.warning("Please login to delete a certification request");
          return;
        }
        this.alert.error("Error deleting certification request, please try again later");
    });
}

}
