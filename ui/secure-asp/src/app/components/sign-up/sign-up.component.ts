import { Component } from '@angular/core';
import {
  AbstractControl,
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  ValidatorFn,
  Validators
} from "@angular/forms";
import {Router, RouterLink} from "@angular/router";
import { NgClass, NgIf} from "@angular/common";
import {AuthService} from "../../services/auth/auth.service";
import {UserRegister} from "../../models/user";
import {AlertService} from "../../services/alert/alert.service";
import {ThemeService} from "../../services/theme/theme.service";
import { ValidationService } from '../../services/validation/validation.service';

@Component({
  selector: 'app-sign-up',
  standalone: true,
  imports: [
    FormsModule,
    ReactiveFormsModule,
    RouterLink,
    NgClass,
    NgIf,
  ],
  templateUrl: './sign-up.component.html',
  styleUrl: './sign-up.component.css'
})
export class SignUpComponent {
  form: FormGroup;

  constructor(private validationService:ValidationService, protected theme:ThemeService, protected auth:AuthService, private router:Router, private alertService:AlertService, private formBuilder: FormBuilder, private authService:AuthService) {
    this.form = this.formBuilder.group({
      fullName: ['', this.validationService.getNameValidator()],
      email: ['', this.validationService.getEmailValidator()],
      password: [''],
      confirmPassword: [''],
      username: ['', this.validationService.getUsernameValidator()],
    });
    this.form.controls['password'].setValidators(this.validationService.getPasswordValidator(this.form));
    this.form.controls['confirmPassword'].setValidators(this.validationService.getConfirmPasswordValidator(this.form));
  }


  signUp() {
    this.alertService.showSpinner();
    const fullName = this.form.controls['fullName'].value;
    const email = this.form.controls['email'].value;
    const password = this.form.controls['password'].value;
    const username = this.form.controls['username'].value;
    if(!fullName || !email || !password || !username) {
      return;
    }
    const user:UserRegister = new UserRegister(email, password, username, fullName);
    this.authService.signUp(user).subscribe(response => {
      this.alertService.success('User registered successfully').then(() => {
        this.router.navigate(['/login']);
      });

    }, error => {
      if(error.status === 422) {
          this.alertService.error('Invalid data, please check the fields');
        return;
      }
      if(error.status === 409) {
      
          this.alertService.error('Username or email already in use');
        return;
      }
      this.alertService.error('Error registering user, please try again later');
    });



  }

  private passwordValidator(): ValidatorFn {
    return (control: AbstractControl): { [key: string]: boolean } | null => {
      if (!this.form ) {
        return null;
      }
      const confirmPassword = this.form.get('confirmPassword')?.value;
      const password = control.value;

      if (confirmPassword !== password) {
        this.form.get('confirmPassword')?.setErrors({ 'notSamePassword': true });
      }else
        this.form.get('confirmPassword')?.setErrors(null);
      return null;
    };
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
}
