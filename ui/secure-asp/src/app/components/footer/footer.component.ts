import { Component, OnDestroy } from '@angular/core';
import {RouterLink} from "@angular/router";
import { ThemeService } from '../../services/theme/theme.service';
import { Subscription } from 'rxjs';
import { NgIf } from '@angular/common';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [
    RouterLink,
    NgIf
  ],
  templateUrl: './footer.component.html',
  styleUrl: './footer.component.css'
})
export class FooterComponent implements OnDestroy{
  show:boolean = true;
  subscription:Subscription;
  constructor(private themeService:ThemeService){
    this.subscription = this.themeService.getShowFooter().subscribe(value => {
      this.show = value;
    });
  }
  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

}
