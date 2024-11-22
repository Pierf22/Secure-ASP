import {
  ActivatedRouteSnapshot,
  CanActivate,
  CanActivateFn, GuardResult,
  MaybeAsync,
  Router,
  RouterStateSnapshot
} from '@angular/router';
import {Injectable} from "@angular/core";
import {AuthService} from "../../services/auth/auth.service";
import {AlertService} from "../../services/alert/alert.service";

@Injectable()
export class NoAuthGuard implements CanActivate{
  constructor(private alert:AlertService, private router:Router, private authService:AuthService) {
  }
  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): MaybeAsync<GuardResult> {
    if(this.authService.getAccessToken() && this.authService.isUser()) {
      this.router.navigate(['/dashboard']);
      return false;
    }else if(this.authService.getAccessToken() && this.authService.isAdmin()) {
      this.router.navigate(['/dashboard/admin']);
      return false;
    }
    else {
      return true
    }
  }

}
