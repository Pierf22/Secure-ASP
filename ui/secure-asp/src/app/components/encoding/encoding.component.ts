import { Component, OnInit } from '@angular/core';
import { AlertService } from '../../services/alert/alert.service';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { PublicProfileService } from '../../services/public-profile/public-profile.service';
import { DatePipe, NgClass, NgForOf, NgIf } from '@angular/common';
import { EncodingService } from '../../services/encoding/encoding.service';
import { UserService } from '../../services/user/user.service';
import {  NgbNavModule, NgbPagination } from '@ng-bootstrap/ng-bootstrap';
import { EncodingPublicDetails } from '../../models/encoding';
import { TagService } from '../../services/tag/tag.service';
import { DomSanitizer } from '@angular/platform-browser';
import { Page } from '../../models/page';
import { ChangeOut } from '../../models/change';
import { AuthService } from '../../services/auth/auth.service';
import { Ownership } from '../../models/ownership';
import { EncodingSettingsComponent } from "../encoding-settings/encoding-settings.component";
import { HttpResponse } from '@angular/common/http';

@Component({
  selector: 'app-encoding',
  standalone: true,
  imports: [NgIf, NgbNavModule, NgForOf, NgClass, RouterLink, NgbPagination, DatePipe, EncodingSettingsComponent],
  templateUrl: './encoding.component.html',
  styleUrl: './encoding.component.css'
})
export class EncodingComponent implements OnInit{



  constructor(private route: ActivatedRoute, private router:Router, private alert:AlertService, private userService:UserService, private tagService:TagService, private safe:DomSanitizer, private encodingService:EncodingService, protected authService:AuthService){}
  username: string = "";
  encodingName: string = "";
  token: string = "";
  noEncoding: boolean = false;
  active = 1;
  page = 1;
  pageSize = 10;
  encoding :EncodingPublicDetails|undefined;
  changes:Page<ChangeOut>= {items: [], page: 1, pages: 1, total: 0, size: 0};


  ngOnInit(): void {
    this.alert.showSpinner();
       this.route.paramMap.subscribe(params => {
      this.username = params.get('username') || "";
      this.encodingName = params.get('encodingName') || "";
      this.token = params.get('token') || "";

    });
    if(this.username && this.encodingName) {
    this.userService.getEncoding(this.username, this.encodingName).subscribe(
      (data) => {
        this.encoding = data;
        this.getChanges();
        this.alert.hideSpinner();
      },
      (error) => {
        this.noEncoding = true;
        this.alert.hideSpinner();
      }
    );}else{
      if(this.token) {
        this.encodingService.getEncodingByToken(this.token).subscribe(
          (data) => {
            this.encoding = data;
            this.getChanges();
            this.alert.hideSpinner();
          },
          (error) => {
            this.noEncoding = true;
            this.alert.hideSpinner();
          }
        );

    }}
  
    
  }
  getChanges() {
    if (!this.encoding) {
      return;
    }
    if(this.token==""){
    this.encodingService.getChanges(this.encoding.id, this.page, this.pageSize).subscribe(
      (data) => {
        this.changes = data;
      },
      (error) => {
        this.alert.error("Error getting changes: " + error);
      });
  }else{
    this.encodingService.getChangesByToken(this.token, this.page, this.pageSize).subscribe(
      (data) => {
        this.changes = data;
      },
      (error) => {
        this.alert.error("Error getting changes: " + error);
      });

  }
}
downloadFile(fileUrl: string | undefined): void {
// Call the service method to download the file
if(!fileUrl)
{
  return;
}
this.encodingService.downloadFile(fileUrl).subscribe(
  (response: HttpResponse<Blob>) => {
    // Extract filename from Content-Disposition header if available
    const contentDisposition = response.headers.get('Content-Disposition');
    let fileName = this.encoding?.name.replaceAll(' ', '-')+'_encrypted.asp'; // Default filename if none is provided

    // Parse filename from Content-Disposition header
    if (contentDisposition && contentDisposition.includes('filename=')) {
      fileName = contentDisposition.split('filename=')[1].trim().replace(/['"]/g, '');
    }

    // Create a temporary URL for the Blob
    const blobUrl = window.URL.createObjectURL(response.body as Blob);

    // Create a temporary link element
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = fileName;
    document.body.appendChild(link);

    // Programmatically click the link to trigger the download
    link.click();

    // Cleanup: Remove the link and revoke the object URL
    document.body.removeChild(link);
    window.URL.revokeObjectURL(blobUrl);
  },
  error => {
    console.error("Failed to download file", error);
  }
);
}

 
    
    getSafeUrl(arg0: string|undefined) {
    return this.safe.bypassSecurityTrustResourceUrl(arg0 || "");
    }
    getTagColor(arg0: string) {
    return this.tagService.getTagColor(arg0);
    }
  
  
    changePage(newPage: number) {
    this.page = newPage;
    this.getChanges();
      }
      notAuthAndOwner(): boolean {
        if (!this.encoding?.user_encodings) {
          return this.authService.isAuthenticated();
        }
        
        for (let i = 0; i < this.encoding.user_encodings.length; i++) {
          const userEncoding = this.encoding.user_encodings[i];
          const isCurrentUser = this.authService.getUsername() === userEncoding.user.username;
          const isOwner = userEncoding.ownership.toString().toUpperCase() === 'OWNER'; 
      
          if (isCurrentUser && isOwner) {
            return true;
          }
        }
        
        return false;
      }
      

}
