import { Component } from '@angular/core';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from "@angular/forms";
import {NgClass, NgIf} from "@angular/common";
import {Router, RouterLink} from "@angular/router";
import {AuthService} from "../../services/auth/auth.service";
import {AlertService} from "../../services/alert/alert.service";
import {ThemeService} from "../../services/theme/theme.service";
import {finalize} from "rxjs";

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    NgIf,
    NgClass,
    RouterLink
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  form:FormGroup;
  constructor(protected theme:ThemeService, private router:Router, private formBuilder: FormBuilder, protected loginService: AuthService, private alertService:AlertService) {
    this.form = this.formBuilder.group({
      username: ['', Validators.compose([Validators.required, Validators.minLength(6)])],
      password: ['', Validators.compose([Validators.required, Validators.minLength(8)])]
    });
    }


  login() {
    this.alertService.showSpinner();
    const username = this.form.get('username')?.value;
    const password = this.form.get('password')?.value;
    if(!username || !password){
      return;
    }
    this.loginService.login(username, password).subscribe(
      response => {
        this.alertService.success('You have successfully logged in').then(() => {
          this.router.navigate(['/']);
        });
      },
      error => {
        if(error.status === 401){
          this.alertService.error('Invalid username or password');
        } else if(error.status === 403){
          this.alertService.error('Your account has been disabled');
        }
        else {
          this.alertService.error('An error occurred please try again later');
        }

      }
    );
  }


}
