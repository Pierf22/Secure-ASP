import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { UserPublicProfile } from '../../models/user';
import { environment } from '../../../enviroment/enviroment';
import { Page } from '../../models/page';
import { UserEncodingOut, UserEncodingPublic } from '../../models/user-encoding';
import { EncodingPublic, EncodingPublicDetails } from '../../models/encoding';

@Injectable({
  providedIn: 'root'
})
export class PublicProfileService {
 
  getUserEncodings(username: string , page: number, pageSize: number):Observable<Page<UserEncodingPublic>>{ 
    return this.http.get<Page<UserEncodingPublic>>(this.backendUsersUrl + '/' + username + '/encodings?page=' + page + '&size=' + pageSize, {responseType: 'json', observe: 'body'});
  }
  private backendUsersUrl = environment.backendUrl+'/v1/public-profiles';


  constructor(private http:HttpClient) { }

  getUserPublicProfile(username: string):Observable<UserPublicProfile>{
    return this.http.get<UserPublicProfile>(this.backendUsersUrl + '/' + username, {responseType: 'json', observe: 'body'});
  }

}
