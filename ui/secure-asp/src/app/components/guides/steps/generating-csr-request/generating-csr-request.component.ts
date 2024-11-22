import { Component } from '@angular/core';
import { NgbAccordionModule } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-generating-csr-request',
  standalone: true,
  imports: [NgbAccordionModule],
  templateUrl: './generating-csr-request.component.html',
  styleUrl: './generating-csr-request.component.css'
})
export class GeneratingCsrRequestComponent {
  protected openFaq=1;

}
