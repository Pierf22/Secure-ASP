import { Injectable } from '@angular/core';
import {HttpClient, HttpErrorResponse, HttpHeaders, HttpResponse} from "@angular/common/http";
import {environment} from "../../../enviroment/enviroment";
import {Observable, tap} from "rxjs";
import {UserRegister} from "../../models/user";
import { Router} from "@angular/router";
import {AlertService} from "../alert/alert.service";

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  setHasSignedCert(arg0: boolean) {
    localStorage.setItem('have_a_signed_cert', arg0.toString());
  }
  getUsername() {
	  return localStorage.getItem('username');
  }
  hasSignedCert(): boolean {
    return localStorage.getItem('have_a_signed_cert') == 'true';
  }

  private loginUrl= environment.backendUrl+"/v1/auth"
  private githubUrl = environment.githubUrl;

  constructor(private alertService:AlertService, private router:Router, private http:HttpClient) { }

  login(username:string, password:string):Observable<HttpResponse<any>>{
    const headers = new HttpHeaders({
      'Authorization': 'Basic ' + btoa(`${username}:${password}`)
    });
    return this.http.post<any>(this.loginUrl+"/login", {}, { headers, observe:"response" })
      .pipe(
        tap(response => {
          this.saveTokens(response);
        })
      );
  }

  signUp(user:UserRegister):Observable<HttpResponse<any>>{
    return this.http.post<HttpResponse<any>>(this.loginUrl+"/sign-up", user, {observe:"response"});
  }
  getAccessToken():string|null{
    return localStorage.getItem('access-token');
  }


  refreshToken(token:string):Observable<HttpResponse<any>>{
    const headers = new HttpHeaders({
      'Refresh-Token': token
    });
    return this.http.post<any>(this.loginUrl+"/refresh-token", {}, {headers, observe:"response"})
      .pipe(
        tap(response => {
          this.saveTokens(response);
        })
      );
  }

  public saveTokens(response: HttpResponse<any>) {
    const authHeader = response.headers.get('Authorization');
    const refreshHeader=response.headers.get('Refresh-Token');
    if (authHeader && refreshHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7);
      this.saveTokensFromString(token, refreshHeader);
    }

  }

  getRefreshToken() {
    return localStorage.getItem('refresh-token');
  }

  deleteTokens() {
    localStorage.removeItem('access-token');
    localStorage.removeItem('refresh-token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('roles');
    localStorage.removeItem('certificated');
    localStorage.removeItem('username');
    localStorage.removeItem('have_a_signed_cert');
  }
  isAuthenticated():boolean{
    return !!this.getAccessToken();
  }
  isAdmin():boolean{
    const roles = localStorage.getItem('roles');
    if (!roles) {
      return false;
    }
    return roles.includes('ROLE_ADMIN');
  }
  isAdminAndUser(): boolean {
    return this.isAdmin() && this.isUser();

  }
  isUser():boolean{
    const roles = localStorage.getItem('roles');
    if (!roles) {
      return false;
    }
    return roles.includes('ROLE_USER');
  }
  isCertificated():boolean {
    const certificated = localStorage.getItem('certificated');
    if (!certificated) {
      return false;
    }
    return certificated == 'true';

  }

  private getUserIdFromToken(token: string) {
    const payload = token.split('.')[1];
    const decodedPayload = atob(payload);
    const payloadObj = JSON.parse(decodedPayload);
    return payloadObj.sub;
  }
  private getUsernameFromToken(token: string) {
    const payload = token.split('.')[1];
    const decodedPayload = atob(payload);
    const payloadObj = JSON.parse(decodedPayload);
    return payloadObj.username;
  }

  private getRolesFromToken(token: string) {
    const payload = token.split('.')[1];
    const decodedPayload = atob(payload);
    const payloadObj = JSON.parse(decodedPayload);
    return payloadObj.roles;
  }

  logout() {
    return this.http.post<any>(this.loginUrl+"/logout", {}, {  observe:"response" })
      .pipe(
        tap(response => {
          this.deleteTokens();
        })
      );
  }

  private saveTokensFromString(accessToken: string, refreshToken: string) {
    localStorage.setItem('access-token', accessToken);
    localStorage.setItem('refresh-token', refreshToken);
    localStorage.setItem('user_id', this.getUserIdFromToken(accessToken) );
    localStorage.setItem('username', this.getUsernameFromToken(accessToken));
    localStorage.setItem('roles', this.getRolesFromToken(accessToken));
    localStorage.setItem('certificated', this.getCertificatedFromToken(accessToken));
    localStorage.setItem('have_a_signed_cert', this.getHaveSignedCertFromToken(accessToken));
    console.log(this.getHaveSignedCertFromToken(accessToken));

  }
  getHaveSignedCertFromToken(accessToken: string): string {
    const payload = accessToken.split('.')[1];
    const decodedPayload = atob(payload);
    const payloadObj = JSON.parse(decodedPayload);
    return payloadObj.have_a_signed_cert;
  }

  oauthLogin() {
    this.alertService.showSpinner();
    const authUrl = this.githubUrl + environment.clientIdGitHub;
    const windowFeatures = 'width=600,height=700,left=200,top=100,resizable,scrollbars=yes,status=1';
    const authWindow=window.open(authUrl, 'GitHub OAuth Login', windowFeatures);
    let accessToken: string;
    let refreshToken: string;



    const checkPopupClosed = setInterval(() => {
      if(authWindow){
        window.addEventListener('message', (event) => {
          if (event.origin === environment.backendUrl && event.data.event=='tokens') {
              accessToken = event.data.accessToken;
              refreshToken = event.data.refreshToken;
            }
        });
      }
      if (authWindow && authWindow.closed) {
        clearInterval(checkPopupClosed);
        if (accessToken && refreshToken) {
          this.saveTokensFromString(accessToken, refreshToken);
          this.alertService.success('You have successfully logged in').then(() => {
            this.router.navigate(['/']);
          });


      }else
        this.alertService.error('An error occurred please try again later');
    }
    }, 1000);
  }

  private getCertificatedFromToken(accessToken: string) {
    const payload = accessToken.split('.')[1];
    const decodedPayload = atob(payload);
    const payloadObj = JSON.parse(decodedPayload);
    return payloadObj.certificated;
  }

  getUserId() {
   return localStorage.getItem('user_id');
  }
}
