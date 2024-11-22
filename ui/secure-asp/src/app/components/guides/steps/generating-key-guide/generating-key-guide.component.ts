import { Component } from '@angular/core';
import { NgbAccordionModule } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-generating-key-guide',
  standalone: true,
  imports: [NgbAccordionModule],
  templateUrl: './generating-key-guide.component.html',
  styleUrl: './generating-key-guide.component.css'
})
export class GeneratingKeyGuideComponent {
  protected openFaq=1;

}
