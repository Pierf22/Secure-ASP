import {Component, inject, OnDestroy, OnInit, TemplateRef} from '@angular/core';
import {NgIf} from "@angular/common";
import {NavigationEnd, Router, RouterLink} from "@angular/router";
import {NgbOffcanvas} from "@ng-bootstrap/ng-bootstrap";
import {ThemeService} from "../../services/theme/theme.service";
import {AuthService} from "../../services/auth/auth.service";
import {AlertService} from "../../services/alert/alert.service";
import { filter, finalize, Subscription } from 'rxjs';

@Component({
  selector: 'app-nav-bar',
  standalone: true,
  imports: [
    NgIf,
    RouterLink,

  ],
  templateUrl: './nav-bar.component.html',
  styleUrl: './nav-bar.component.css'
})
export class NavBarComponent implements OnDestroy, OnInit{
  show:boolean = true;
  subscription:Subscription;
  constructor( private router:Router, private alert:AlertService, protected theme:ThemeService, protected auth:AuthService) {
    this.subscription = this.theme.getShowNavbar().subscribe(value => {
      this.show = value;
    });
  }
  ngOnInit(): void {
    this.router.events
    .pipe(
      filter(event => event instanceof NavigationEnd) 
    )
    .subscribe((event: NavigationEnd) => {
     this.theme.setTheme();
    });
  }
  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }
  private offcanvasService = inject(NgbOffcanvas);



  open(content: TemplateRef<any>) {
    this.offcanvasService.open(content, {position: 'end'});

  }


  doLogout(offcanvas: any) {
    this.alert.showSpinner();
    offcanvas.close();
    this.auth.logout().pipe(
      finalize(() => {
        this.alert.hideSpinner();
        this.alert.success("Logout successful").then(() => {
          this.router.navigate(['/home']);
        });
      })
    ).subscribe(
      () => {
        this.alert.hideSpinner();
      },
      error => {
        this.alert.hideSpinner();
      }
    );

  }
}
