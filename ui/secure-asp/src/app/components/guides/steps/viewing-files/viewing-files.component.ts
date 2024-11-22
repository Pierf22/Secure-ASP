import { Component } from '@angular/core';
import { NgbAccordionModule } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-viewing-files',
  standalone: true,
  imports: [NgbAccordionModule],
  templateUrl: './viewing-files.component.html',
  styleUrl: './viewing-files.component.css'
})
export class ViewingFilesComponent {
protected openFaq=1;
}
