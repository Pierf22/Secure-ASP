import { Component } from '@angular/core';
import { NgbAccordionModule } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-upload-files',
  standalone: true,
  imports: [NgbAccordionModule],
  templateUrl: './upload-files.component.html',
  styleUrl: './upload-files.component.css'
})
export class UploadFilesComponent {
  protected openFaq=1;

}
