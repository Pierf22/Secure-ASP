import {
  ActivatedRouteSnapshot,
  CanActivate,
  CanActivateFn,
  GuardResult,
  MaybeAsync, Router,
  RouterStateSnapshot
} from '@angular/router';
import {Injectable} from "@angular/core";
import {AuthService} from "../../services/auth/auth.service";

@Injectable()
export class AuthGuard implements CanActivate{
  constructor(private router:Router, private authService:AuthService) {
  }
  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): MaybeAsync<GuardResult> {
    if(this.authService.getAccessToken())
      return true
    else {
      this.router.navigate(['/login'])
      return false
    }
  }

}
