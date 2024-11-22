import {
  HttpClient,
  HttpErrorResponse,
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest
} from '@angular/common/http';
import {AuthService} from "../../services/auth/auth.service";
import {catchError, Observable, switchMap, tap, throwError} from "rxjs";
import {Router} from "@angular/router";
import {AlertService} from "../../services/alert/alert.service";
import {Injectable} from "@angular/core";
@Injectable()
export class TokenInterceptor implements HttpInterceptor{
  constructor(private http:HttpClient, private alert:AlertService, private router:Router, private authService:AuthService) {
  }
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = this.authService.getAccessToken();
    if (!token) {
      return next.handle(req);
    }
    if(req.url.includes('login') || req.url.includes('refresh-token')){
      return next.handle(req);
    }

    const authReq = req.clone({
      headers: req.headers.set('Authorization', `Bearer ${token}`),
    });

    return next.handle(authReq).pipe(
      catchError((error) => {
        if (error instanceof HttpErrorResponse && error.status === 401) {
          const refreshToken = this.authService.getRefreshToken();
          if (refreshToken) {
            return this.authService.refreshToken(refreshToken).pipe(
              switchMap((response) => {
                this.authService.saveTokens(response);
                const newToken = this.authService.getAccessToken();
                const newAuthReq = req.clone({
                  headers: req.headers.set('Authorization', `Bearer ${newToken}`),
                });
                return next.handle(newAuthReq);
              }),
              catchError((refreshError) => {
                if (refreshError instanceof HttpErrorResponse && refreshError.status === 401) {
                  this.authService.deleteTokens();
                  this.router.navigate(['login']);
                } else {
                  this.authService.deleteTokens();
                  this.alert.error("Error during the completion of the request, please try again later.").then(() => {
                    this.router.navigate(['home']);
                  });
                }
                return throwError(refreshError);
              })
            );
          } else {
            this.authService.deleteTokens();
            this.router.navigate(['login']);
          }
        }
        return throwError(error);
      })
    );
  }

}
