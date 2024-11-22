import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  setTheme(): void {
    const savedTheme = localStorage.getItem('theme');
    
    if (savedTheme) {
      document.documentElement.setAttribute('data-bs-theme', savedTheme);
    } else {
      const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)').matches;
      
      if (prefersDarkScheme) {
        document.documentElement.setAttribute('data-bs-theme', 'dark');
      } else {
        document.documentElement.setAttribute('data-bs-theme', 'light');
      }
    }}
    showNavbar:BehaviorSubject<boolean>;
    showFooter:BehaviorSubject<boolean>;
  

    setShowNavbar(value:boolean) {
      this.showNavbar.next(value);
    }
    setShowFooter(value:boolean) {
      this.showFooter.next(value);
    }
    getShowNavbar() {
      return this.showNavbar;
    }
    getShowFooter() {
      return this.showFooter;
    }

  constructor() { 
    this.showNavbar = new BehaviorSubject<boolean>(true);
    this.showFooter = new BehaviorSubject<boolean>(true);
  }
  changeTheme(): void {
    let theme = document.documentElement.getAttribute('data-bs-theme');
    if (theme === 'dark') {
      document.documentElement.setAttribute('data-bs-theme', 'light');
      localStorage.setItem('theme', 'light');
    } else {
      document.documentElement.setAttribute('data-bs-theme', 'dark');
      localStorage.setItem('theme', 'dark');
    }
  }

  darkMode() {
    return document.documentElement.getAttribute('data-bs-theme') === 'dark';
  }
}
