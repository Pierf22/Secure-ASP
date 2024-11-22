import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../../enviroment/enviroment';

@Injectable({
  providedIn: 'root'
})
export class RoleService {
  constructor(private http:HttpClient) { }


  getRoles() {
    return this.http.get<string[]>(environment.backendUrl+'/v1/roles', {observe: 'body'});
  }
}
