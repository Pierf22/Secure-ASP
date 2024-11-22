import { Component, inject, Input, OnInit } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { User, UserEdit } from '../../../models/user';
import { FormArray, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ValidationService } from '../../../services/validation/validation.service';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { NgClass, NgFor, NgIf } from '@angular/common';
import { NgbNavModule } from '@ng-bootstrap/ng-bootstrap';
import { RoleService } from '../../../services/role/role.service';
import { AlertService } from '../../../services/alert/alert.service';
import { UserService } from '../../../services/user/user.service';
import { CertificationEdit, CertificationRequest } from '../../../models/certification-request';
import { CertificationRequestService } from '../../../services/certification-request/certification-request.service';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { environment } from '../../../../enviroment/enviroment';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-admin-modify-user-modal',
  standalone: true,
  imports: [FormsModule,  ReactiveFormsModule, NgClass, NgIf, NgbNavModule, NgFor, RouterLink],
  templateUrl: './admin-modify-user-modal.component.html',
  styleUrl: './admin-modify-user-modal.component.css'
})
export class AdminModifyUserModalComponent implements OnInit {
noChangeFormCertification() {
return this.formCertificationData.get('status')?.value === this.certificationRequest?.status && this.formCertificationData.get("denialReason")?.value === this.certificationRequest?.denied_reason;
}
modifyCertification() {
this.alert.showSpinner();
const status = this.formCertificationData.value.status;
const id = this.certificationRequest?.id;
if(!id) {
  return;
}
let denialReason = this.formCertificationData.value.denialReason;
if (denialReason === '' || status !== 'Rejected') {
  denialReason = null;
}
const certification = new CertificationEdit(status, denialReason);
this.certificationService.editCertificationRequest(id, certification).subscribe(
  (data) => {
    this.alert.hideSpinner();
    this.modified = true;
    this.activeModal.close(this.modified);
    this.alert.successToast('Certification modified successfully');
  },
  (error) => {
    this.alert.hideSpinner();
    this.activeModal.close(this.modified);
    if(error.status === 401) {
      this.alert.warning('Your session has expired, please login again');
      return;
    }
    this.alert.error('Error modifying certification, please try again later');
  }
);

  
}



  activeModal = inject(NgbActiveModal);
  active="top";
  modified = false;
  front_type:string = '';
  back_type:string = '';
  front_url:string= '';
  back_url:string = '';

  certificationRequest: CertificationRequest | undefined;
  roles: string[] = [];
  status: string[] = [];
  formUserData:FormGroup;
  formCertificationData:FormGroup;
  constructor(  private certificationService:CertificationRequestService ,private userService:UserService, private alert:AlertService, private fb:FormBuilder, private validatorService:ValidationService, private roleService:RoleService, private router:Router) {
    this.formUserData = this.fb.group({
      username: ['', this.validatorService.getUsernameValidator()],
      email: ['', this.validatorService.getEmailValidator()],
      fullName: ['', this.validatorService.getNameValidator()],
      disabled: [false, Validators.required],
      password: [''],
      roles: this.fb.array([], Validators.required)

    });
    this.formUserData.get('password')?.setValidators( this.validatorService.getPasswordValidatorWithoutRequired(this.formUserData));
    this.formCertificationData = this.fb.group({
      status: ['', Validators.required],
      denialReason: ['']
    });
   }




  ngOnInit(): void {
    this.loadRoles();
    this.getCertificationRequest();
    this.loadStatus();

  }
  async getCertificationRequest() {
    await this.certificationService.getCertificationRequest(this.user.id).subscribe(
      data => {

        this.certificationRequest= data;
        this.formCertificationData.patchValue({
          status: this.certificationRequest.status,
          denialReason: this.certificationRequest.denied_reason});
        if(this.certificationRequest.back_url!=null){
          this.certificationService.loadFile(this.certificationRequest.back_url).subscribe(
            data => {
              this.back_type = data.type;
              this.back_url = URL.createObjectURL(data);
            },
            error => {
              this.alert.error("Error loading back file, please try again later");
            }
          );
        }
        if(this.certificationRequest.front_url!=null){
          this.certificationService.loadFile(this.certificationRequest.front_url).subscribe(
            data => {
              this.front_type = data.type;
              this.front_url = URL.createObjectURL(data);
            },
            error => {
              this.alert.error("Error loading front file, please try again later");
            }
          );}
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
  loadRoles() {
    this.alert.showSpinner();
    this.roleService.getRoles().subscribe(roles => {
      this.roles = roles;
      this.loadForm();
      this.alert.hideSpinner();
    }, error => {
      this.alert.error('Failed to load roles, please try again later');
      this.activeModal.close();
  });
}
  loadForm() {
    this.formUserData.patchValue({
      username: this.user.username,
      email: this.user.email,
      fullName: this.user.full_name,
      disabled: this.user.disabled
    });
    this.roles.forEach(role => {
      this.rolesFormArray.push(this.fb.group({
        name: role,
        checked: this.user.roles.includes(role)
      }));
    });
  }

	@Input() user!: User;
  get rolesFormArray() {
    return this.formUserData.get('roles') as FormArray;
  }
  noChangeFormData() {
    let check1 = this.formUserData.value.username === this.user.username &&
    this.formUserData.value.email === this.user.email &&
    this.formUserData.value.fullName === this.user.full_name &&
    this.formUserData.value.disabled === this.user.disabled  ;
    
    let check2 = true;

    for(let i = 0; i < this.rolesFormArray.length; i++) {
    const isChecked = this.rolesFormArray.at(i).get("checked")?.value;
    const roleName = this.rolesFormArray.at(i).value.name;
    const userHasRole = this.user.roles.includes(roleName);

    if(isChecked !== userHasRole) {
    check2 = false;
    break;
    }
    }

    return check1 && check2 ;
  }
  noRolesSelected() {
    for(let i = 0; i < this.rolesFormArray.length; i++) {
      if(this.rolesFormArray.at(i).get("checked")?.value) {
        return false;
      }
    }
    return true;
  }
  protected modifyUser() {
    this.alert.showSpinner();
    let fullName : string | undefined;
    let email: string | undefined;
    let username: string | undefined;
    let password: string | undefined;
    let disabled: boolean | undefined;
    let roles: string[] | undefined;
    if(this.formUserData.controls['fullName'].value!=this.user.full_name){
      fullName = this.formUserData.controls['fullName'].value;
    }
    if(this.formUserData.controls['email'].value!=this.user.email){
      email = this.formUserData.controls['email'].value;
    }
    if(this.formUserData.controls['username'].value!=this.user.username){
      username = this.formUserData.controls['username'].value;
    }
    if(this.formUserData.controls['password'].value!=''  ){
      password = this.formUserData.controls['password'].value;
    }
    if(this.formUserData.controls["disabled"].value != this.user.disabled){
      disabled = this.formUserData.controls["disabled"].value;
    }
    for(let i = 0; i < this.rolesFormArray.length; i++) {
      if(this.rolesFormArray.at(i).get("checked")?.value) {
        if(!roles) {
          roles = [];
        }
        roles.push(this.rolesFormArray.at(i).value.name);
      }
    }
    const user = new UserEdit(email, username, fullName, password, disabled, roles);
    this.userService.editUser(this.user.id, user).subscribe(
      (data)=>{
        this.alert.hideSpinner();
        this.modified = true;
        this.activeModal.close(this.modified);
        this.alert.successToast('User modified successfully');
        
      },
      (error)=>{
        this.alert.hideSpinner();
        if(error.status === 401){
          this.alert.warning('You session has expired, please login again');
          return;
        }
        this.alert.error('Error modifying user, please try again later');
      }
    );
  }
  loadStatus() {
    this.certificationService.getStatus().subscribe(status => {
      this.status = status;
      this.formCertificationData.valueChanges.subscribe(() => {
        this.updateDenialReasonValidator();
      });
    }, error => {
      this.alert.error('Failed to load status, please try again later');
    });
  }

  
  updateDenialReasonValidator(){
    const status = this.formCertificationData.get('status')?.value;
    if(status === 'Rejected') {
      return false;}
    return true;}
    }





