import {Component, inject, OnInit, TemplateRef} from '@angular/core';
import {UserService} from "../../services/user/user.service";
import {AuthService} from "../../services/auth/auth.service";
import {ActivatedRoute, Router, RouterLink} from "@angular/router";
import {UserEdit, UserProfile} from "../../models/user";
import {AlertService} from "../../services/alert/alert.service";
import {NgClass, NgIf} from "@angular/common";
import {
  AbstractControl,
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  ValidatorFn,
  Validators
} from "@angular/forms";
import {NgbModal, NgbNavModule} from "@ng-bootstrap/ng-bootstrap";
import { ValidationService } from '../../services/validation/validation.service';
import  JSZip from 'jszip';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [
    NgIf,
    FormsModule,
    NgClass,
    ReactiveFormsModule,
    NgbNavModule,
    RouterLink
  ],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css'
})
export class ProfileComponent implements OnInit{

  uploadCertFile($event: Event) {
    let file = ($event.target as HTMLInputElement).files?.item(0);
    const max_size = 10 * 1024 * 1024; // 10MB
  
    if (file) {
      // Check file extension
      const validExtensions = ['.pem'];
      const fileExtension = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
      
      if (!validExtensions.includes(fileExtension)) {
        console.log('Invalid file extension');
        // Reset the file input
        ($event.target as HTMLInputElement).value = ''; // Clear the input
        return;
      }
      // Check file size
      if (file.size > max_size) {
        this.formUploadCertificate.get('certificate')?.setErrors({ 'max_size': true });
        console.log('File size exceeds the limit');
        return;
      } else {
        // Clear previous errors and patch the file
        this.formUploadCertificate.get('certificate')?.setErrors(null);
        this.formUploadCertificate.patchValue({ certificate: file });
      }
    }
  }
  

  protected active = "userInfo";
  protected form:FormGroup;
  protected formUploadCertificate:FormGroup;
  protected user:UserProfile=new UserProfile({email:'',username:'',full_name:'',oauth2_user:false});
  constructor(private validationService:ValidationService, private fb:FormBuilder, private alert:AlertService, private router:Router, private userService: UserService, protected authService:AuthService, private route:ActivatedRoute) {
    this.form = this.fb.group({
      fullName: ['', this.validationService.getNameValidator()],
      email: ['', this.validationService.getEmailValidator()],
      username: ['', this.validationService.getUsernameValidator()],
      password: ['', ],
      confirmPassword: [''],
    });
    this.formUploadCertificate = this.fb.group({
      certificate: [null, Validators.required],
    });
    this.form.controls['password'].setValidators(this.validationService.getPasswordValidatorWithoutRequired(this.form));
    this.form.controls['confirmPassword'].setValidators(this.confirmPasswordValidator());
  }
  private modalService = inject(NgbModal);

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      if(params['start']){
        this.active = params['start'];
      }
    });
    const userId = this.authService.getUserId();
    if(!userId){
      this.router.navigate(['/login']);
      return;
    }
    this.alert.showSpinner();
    this.userService.getUser(userId).subscribe((data)=>{
      this.user = new UserProfile(data);
      this.alert.hideSpinner();
    }, (error)=>{
      this.alert.hideSpinner();
      if(error.status === 401){
        this.router.navigate(['/login']);
        return;}
      this.alert.error('Error loading user profile, please try again later').then(()=>{this.router.navigate(['/login']);});

    });
  }



  openDeletionModal(deleteConfirmation: TemplateRef<any>) {
    this.modalService.open(deleteConfirmation).result.then(
      (result) => {
        const userId = this.authService.getUserId();
        if(!userId){
          this.router.navigate(['/login']);
          return;
        }
       this.alert.showSpinner();
        this.userService.deleteUser(userId).subscribe(
          (data)=>{
            this.alert.hideSpinner();
            this.authService.deleteTokens();
            this.alert.success('User deleted successfully').then(()=>{this.router.navigate(['/login']);});
          },
          (error)=>{
            this.alert.hideSpinner();
            if(error.status === 401){
              this.router.navigate(['/login']);
              return;
            }
            this.alert.error('Error deleting user, please try again later');
          }
        );
      },(ignored)=>{

      }
    );

  }

  openEditModal(editProfile: TemplateRef<any>) {
    this.form.controls['fullName'].setValue(this.user.full_name);
    this.form.controls['email'].setValue(this.user.email);
    this.form.controls['username'].setValue(this.user.username);
    this.modalService.open(editProfile).result.then(
      (result) => {
        if(this.form.invalid){
          return;
        }
        this.alert.showSpinner();
        let fullName : string | undefined;
        let email: string | undefined;
        let username: string | undefined;
        let password: string | undefined;
        if(this.form.controls['fullName'].value!=this.user.full_name){
          fullName = this.form.controls['fullName'].value;
        }
        if(this.form.controls['email'].value!=this.user.email){
          email = this.form.controls['email'].value;
        }
        if(this.form.controls['username'].value!=this.user.username){
          username = this.form.controls['username'].value;
        }
        if(this.form.controls['password'].value && this.form.controls['password'].valid && this.form.controls['confirmPassword'].valid ){
          password = this.form.controls['password'].value;
        }

        const newUser = new UserEdit(email, username, fullName, password, undefined, undefined);
        const userId = this.authService.getUserId();
        if(!userId){
          this.router.navigate(['/login']);
          return;
        }
        this.userService.editUser(userId, newUser).subscribe(
          (data)=>{
            this.alert.hideSpinner();
            if(password || username){
              this.authService.deleteTokens();
              this.alert.success('User updated successfully').then(()=>{this.router.navigate(['/login']);});
              return;
            }
            this.alert.success('User updated successfully').then(()=>{this.ngOnInit();});
          },
          (error)=>{
            this.alert.hideSpinner();
            if(error.status === 401){
              this.router.navigate(['/login']);
              return;
            }
            if(error.status === 422){
              this.alert.error('Invalid data, please check the fields');
              return;
            }
            if(error.status === 409){
              this.alert.error('Username or email already in use');
              return;
            }
            this.alert.error('Error updating user, please try again later');
          }
        );

      },(ignored)=>{

      }
    );

  }

  noChange() {
    return (this.form.controls['fullName'].value === this.user.full_name && this.form.controls['email'].value === this.user.email && this.form.controls['username'].value === this.user.username &&  this.form.controls['password'].invalid) ;
  }
  private confirmPasswordValidator(): ValidatorFn {
    return (control: AbstractControl): { [key: string]: boolean } | null => {
      if (!this.form ) {
        return null;
      }
      const confirmPassword = control.value;
      const password = this.form.get('password')?.value;

      if (confirmPassword !== password) {
        return { 'notSamePassword': true };
      }
      return null;
    };
  }


goToPublicProfile() {
  const username = this.user.username;
  this.router.navigate(['/'+username,]);
  }
  uploadRequest() {
    const file = this.formUploadCertificate.get('certificate')?.value;
    const userId = this.authService.getUserId();
    if(!userId){
      this.router.navigate(['/login']);
      return;
    }
    if(!file){
      this.alert.error('Please select a file');
      return;
    }
   

// Function to send the CSR request and download the file
this.userService.saveCsrRequest(userId, file).subscribe(
  (data: Blob) => {
    // Create a blob from the response
    const fileName = 'certificate.pem'; // Define the file name
    const blob = new Blob([data], { type: 'application/x-pem-file' }); // Set the correct MIME type

    // Create a temporary URL for the Blob
    const downloadUrl = window.URL.createObjectURL(blob);

    // Create a temporary <a> element to trigger the download
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = fileName; // Set the file name for the download

    // Append the link to the DOM, trigger a click, and then remove the link
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Revoke the object URL after the download
    window.URL.revokeObjectURL(downloadUrl);

    // Show a success message to the user
    this.alert.success('Certificate request uploaded and file downloaded successfully');
    this.authService.setHasSignedCert(true);
  },
  (error) => {
    if (error.status === 401) {
      this.router.navigate(['/login']);
      return;
    }
    this.alert.error('Error uploading certificate request, please try again later');
  }
);
  }
}


