import { Component } from '@angular/core';
import { NgbAccordionModule } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-signing-files',
  standalone: true,
  imports: [NgbAccordionModule],
  templateUrl: './signing-files.component.html',
  styleUrl: './signing-files.component.css'
})
export class SigningFilesComponent {
  protected openFaq=1;

}
