import {Component} from '@angular/core';
import {NgIf} from '@angular/common';
import {CertificationRequestDetailsComponent} from "../certification-request-details/certification-request-details.component";
import {AuthService} from "../../services/auth/auth.service";
import { Router } from '@angular/router';
import { EncodingsComponent } from "../encodings/encodings.component";

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [NgIf, CertificationRequestDetailsComponent,
    EncodingsComponent
],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {
	isCertificated(): any {
	if(this.authService.isCertificated()){
		this.router.navigate(['/encodings']);
	}else
return this.authService.isCertificated();
}
constructor(private authService: AuthService, private router: Router) {


}
}

