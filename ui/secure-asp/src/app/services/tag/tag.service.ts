import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class TagService {
  tagColors: string[] = ["orange", "info", "success", "danger", "warning", "info", "light", "dark", "orange"];
	tagColorMap: { [key: string]: string } = {}; 
  colorIndex: number = 0;


  constructor() { }
  getTagColor(name: string):string{
    if (!this.tagColorMap[name]) {
      this.tagColorMap[name] = this.tagColors[this.colorIndex];
      this.colorIndex = (this.colorIndex + 1) % this.tagColors.length; // Randomize the color for the next tag
      }
      return this.tagColorMap[name];
  }
}
