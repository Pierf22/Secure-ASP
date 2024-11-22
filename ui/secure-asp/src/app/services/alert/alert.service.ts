import { Injectable } from '@angular/core';
import Swal from 'sweetalert2'
import {ThemeService} from "../theme/theme.service";
import { Router } from '@angular/router';
@Injectable({
  providedIn: 'root'
})
export class AlertService {





  constructor(private theme:ThemeService, private router:Router) { }

  success(name: string) {
    let background_color = 'white';
    let color = '#212529';
  if(this.theme.darkMode()){
    background_color = '#212529';
    color = 'white';
  }
  return Swal.fire({
    icon: 'success',
    title: name,
    background: background_color,
    color: color,
    confirmButtonColor: '#2B4F81',

  })
  }

  error(name: string) {
    let background_color = 'white';
    let color = '#212529';
    if(this.theme.darkMode()){
      background_color = '#212529';
      color = 'white';
    }
  return Swal.fire({
    icon: 'error',
    title: name,
    background: background_color,
    color: color,
    confirmButtonColor: '#2B4F81'
  })

  }
 
  


  showSpinner() {
    let color = '#212529';
    if(this.theme.darkMode()){
      color = 'white';
    }
    return Swal.fire({
      background: 'rgb(0,0,0,0)',
      allowOutsideClick: false,
      showConfirmButton: false,
      color: color,
      title: 'Loading...',
      html: '<div style="overflow: hidden;"> <div class="spinner-border text-primary" style="width: 5rem; height: 5rem;" role="status"> </div></div>',
    })

  }

  hideSpinner() {
    Swal.close();
  }
  warning(text: string) {
    let background_color = 'white';
    let color = '#212529';
    if(this.theme.darkMode()){
      background_color = '#212529';
      color = 'white';
    }
    return Swal.fire({
      icon: 'warning',
      title: text,
      background: background_color,
      color: color,
      confirmButtonColor: '#2B4F81'
  });}
  successToast(name: string) {
    let background_color = 'white';
    let color = '#212529';
    if(this.theme.darkMode()){
      background_color = '#212529';
      color = 'white';
    }
    return Swal.fire({
      icon: 'success',
      title: name,
      background: background_color,
      color: color,
      position: 'top-start',
      confirmButtonColor: '#2B4F81',
      toast: true,
      showConfirmButton: false,
      timer: 3000,
      timerProgressBar: true
    })
  }
  errorToast(name: string) {
    let background_color = 'white';
    let color = '#212529';
    if(this.theme.darkMode()){
      background_color = '#212529';
      color = 'white';
    }
    return Swal.fire({
      icon: 'error',
      title: name,
      background: background_color,
      color: color,
      confirmButtonColor: '#2B4F81',
      toast: true,
      position: 'top-start',
      showConfirmButton: false,
      timer: 3000,
      timerProgressBar: true
    })
  }
}
