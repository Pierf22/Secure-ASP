import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { UserService } from '../../services/user/user.service';
import { PublicProfileService } from '../../services/public-profile/public-profile.service';
import { UserPublicProfile } from '../../models/user';
import { AlertService } from '../../services/alert/alert.service';
import { NgClass, NgForOf, NgIf } from '@angular/common';
import { TagService } from '../../services/tag/tag.service';
import { Page } from '../../models/page';
import { EncodingPublic } from '../../models/encoding';
import { UserEncodingPublic } from '../../models/user-encoding';
import { NgbPagination } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-public-user-profile',
  standalone: true,
  imports: [NgForOf, NgIf, RouterLink, NgClass, NgbPagination],
  templateUrl: './public-user-profile.component.html',
  styleUrl: './public-user-profile.component.css'
})
export class PublicUserProfileComponent implements OnInit {


getTagColor(arg0: string): string {
return this.tagService.getTagColor(arg0);
}
  username: string="";
  userNotFound: boolean = false;
  publicProfile: UserPublicProfile|null = null;
  encodings: Page<UserEncodingPublic>|null = null;

  constructor(private route: ActivatedRoute, private router:Router, private publicProfileService:PublicProfileService, private alert:AlertService, private tagService:TagService) {}

  ngOnInit() {
    // Access the 'username' route parameter
    this.route.paramMap.subscribe(params => {
      this.username = params.get('username') || "";
    });
    this.getUser();
    this.getEncodings();
  }
  getUser() {
    if(this.username=="") {
      return;
    }
    this.publicProfileService.getUserPublicProfile(this.username).subscribe(
      (data) => {
        this.publicProfile = data;
      },
      (error) => {
        if(error.status == 404) {
          this.userNotFound = true;
         return;
        }
      }
    );
  }


  getEncodings(page: number = 1, pageSize: number = 10) {
    if(this.username=="") {
      return;
    }
    this.publicProfileService.getUserEncodings(this.username, page, pageSize).subscribe(
      (data) => {
        this.encodings = data;
      },
      (error) => {
        if(error.status == 404) {
         return;
        }else{
          this.alert.errorToast("Failed to get encodings");
        }
      }
    );
    
    }

    
}
