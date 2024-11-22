import { Injectable } from '@angular/core';
import { AbstractControl, ValidatorFn, Validators } from '@angular/forms';

@Injectable({
  providedIn: 'root'
})
export class ValidationService {


  constructor() { }

  // Full Name Validator
  getNameValidator() {
    return Validators.compose([
      Validators.required, 
      Validators.minLength(2), 
      Validators.pattern('^[a-zA-Z][a-zA-Z ]*$')
    ]);
  }

  // Email Validator
  getEmailValidator() {
    return Validators.compose([
      Validators.required, 
      Validators.email
    ]);
  }

  // Password Validator
  getPasswordValidator(form: any) {
    return Validators.compose([
      Validators.required, 
      Validators.minLength(8), 
      Validators.pattern('^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[\\W_])[a-zA-Z\\d\\W_]{8,64}$'), 
      this.passwordValidator(form)
    ]);
  }
  // Password Validator without required
  getPasswordValidatorWithoutRequired(form: any) {
    return Validators.compose([
      Validators.minLength(8), 
      Validators.pattern('^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[\\W_])[a-zA-Z\\d\\W_]{8,64}$'), 
      this.passwordValidator(form)
    ]);
  }

  // Custom Validator to check if password and confirm password match
  private passwordValidator(form: any): ValidatorFn {
    return (control: AbstractControl): { [key: string]: boolean } | null => {
      if (!form) {
        return null;
      }
      const confirmPassword = form.get('confirmPassword')?.value;
      const password = control.value;

      if (confirmPassword !== password) {
        form.get('confirmPassword')?.setErrors({ 'notSamePassword': true });
      } else {
        form.get('confirmPassword')?.setErrors(null);
      }
      return null;
    };
  }
  getConfirmPasswordValidator(form: any): ValidatorFn {
    return (control: AbstractControl): { [key: string]: boolean } | null => {
      if (!form ) {
        return null;
      }
      const confirmPassword = control.value;
      const password = form.get('password')?.value;

      if (confirmPassword !== password) {
        return { 'notSamePassword': true };
      }
      return null;
    };
  }
  getUsernameValidator() {
    return Validators.compose([
      Validators.required, 
      Validators.minLength(6), 
      Validators.pattern('^[a-zA-Z][a-zA-Z0-9-]*$')
    ]);
  }
}

