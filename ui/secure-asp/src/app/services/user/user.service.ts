import { Injectable } from '@angular/core';
import {HttpClient, HttpParams} from "@angular/common/http";
import {environment} from "../../../enviroment/enviroment";
import {User, UserCount, UserEdit, UserKeys, UserPublicProfile, UserUsername} from "../../models/user";
import { Observable } from 'rxjs';
import { Page, Order } from '../../models/page';
import { serialize } from 'object-to-formdata';
import {UserEncodingOut} from "../../models/user-encoding";
import { Encoding, EncodingPublicDetails } from '../../models/encoding';

@Injectable({
  providedIn: 'root'
})
export class UserService {

	getEncodings(userId: string, page: number, size: number, sort: string, order: Order, name?:string, tags?:string[], startUploadData?:Date, endUploadDate?:Date):Observable<Page<UserEncodingOut>> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('size', size.toString());
    if(sort) {
      params = params.set('sort', sort);
      params = params.set('order', order);
    }
    if(name) {
      params = params.set('name', name);
    }
    if(tags) {
      for(let tag of tags) {
        params = params.append('tags', tag);
      }
    }
    if (startUploadData) {
      params = params.set('start-upload-date', startUploadData.toISOString().split('T')[0]);
    }
    if (endUploadDate) {
      params = params.set('end-upload-date', endUploadDate.toISOString().split('T')[0]);
    }
    
		return this.http.get<Page<UserEncodingOut>>(this.backendUsersUrl + '/' + userId + '/encodings', {params: params, responseType: 'json', observe: 'body'});
	}

  getUsers(page: number, size: number, sort: string, order: Order, username:string|null, email:string|null, full_name:string|null ): Observable<Page<User>> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('size', size.toString());
  
    if (sort) {
      params = params.set('sort', sort);
      params = params.set('order', order);
    }
    if (username) {
      params = params.set('username', username);
    }
    if (email) {
      params = params.set('email', email);
    }
    if (full_name) {
      params = params.set('full-name', full_name);
    }
  
    return this.http.get<Page<User>>(this.backendUsersUrl, { params: params, responseType: 'json', observe: 'body' });
  }




  private backendUsersUrl = environment.backendUrl + '/v1/users';

  constructor(private http:HttpClient) { }

  getUser(userId: string) {
    return this.http.get(this.backendUsersUrl + '/' + userId, {responseType: 'json', observe: 'body'});

  }

  deleteUser(userId: string) {
    return this.http.delete(this.backendUsersUrl + '/' + userId, {responseType: 'json', observe: 'body'});

  }

  editUser(userId: string, newUser: UserEdit) {
    return this.http.patch(this.backendUsersUrl + '/' + userId, newUser, {responseType: 'json', observe: 'body'});

  }
  getUserCount() :Observable<UserCount> {
    return this.http.get<UserCount>(this.backendUsersUrl + '/count', {responseType: 'json', observe: 'body'});
  }



  getUsernames(searchText: string|null): Observable<Page<UserUsername>> {
    if (!searchText) 
      return this.http.get<Page<UserUsername>>(this.backendUsersUrl + '/usernames', { responseType: 'json', observe: 'body' });
    return this.http.get<Page<UserUsername>>(this.backendUsersUrl + '/usernames', { params: { value: searchText, size:10 }, responseType: 'json', observe: 'body' });
  }
    saveEncoding(userId:string, encodingToSave: Encoding) {
      const options = {
        noAttributesWithArrayNotation: true
      }

      const formData = serialize(encodingToSave, options);
      return this.http.post(this.backendUsersUrl + '/' + userId + '/encodings', formData, {responseType: 'json', observe: 'body'});
    }
    getEncoding(username: string, encodingName: string):Observable<EncodingPublicDetails> {
      return this.http.get<EncodingPublicDetails>(this.backendUsersUrl + '/'  +username+"/"+ encodingName, {responseType: 'json', observe: 'body'});
    }
    saveCsrRequest(userId: string, file: any) {
      const options = {
        noAttributesWithArrayNotation: true
      }

      const formData = new FormData();
      formData.append('file', file);
      return this.http.post(this.backendUsersUrl + '/' + userId + '/csr-request', formData, {responseType: 'blob', observe: 'body'});
    }
  
}
