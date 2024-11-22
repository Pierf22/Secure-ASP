import { HttpClient, HttpResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../../enviroment/enviroment';
import { Observable } from 'rxjs';
import { Page } from '../../models/page';
import { TagName } from '../../models/tag';
import { EncodingChanges, EncodingCount, EncodingPublicDetails } from '../../models/encoding';
import { ChangeOut } from '../../models/change';
import { EncodingToken } from '../../models/token';
import { serialize } from 'object-to-formdata';


@Injectable({
  providedIn: 'root'
})
export class EncodingService {


  private encodingUrl = environment.backendUrl + '/v1/encodings';


  constructor(private http:HttpClient) { }
  getEncodingsCount():Observable<EncodingCount> {
    return this.http.get<EncodingCount>(this.encodingUrl + '/count', { responseType: 'json', observe: 'body' });
  }
  downloadFile(fileUrl: string): Observable<HttpResponse<Blob>> {
    return this.http.get(fileUrl, {
      responseType: 'blob',      // Specify that the response is a Blob
      observe: 'response'        // Observe the full response to access headers
    });
  }

  getTags(searchText: string|null):Observable<Page<TagName>> {
    if (!searchText) 
      return this.http.get<Page<TagName>>(this.encodingUrl + '/tags', { responseType: 'json', observe: 'body' });
    return this.http.get<Page<TagName>>(this.encodingUrl + '/tags', { params: { value: searchText, size:10 }, responseType: 'json', observe: 'body' });
  }

  getChanges(encodingId:string, page:number, size:number):Observable<Page<ChangeOut>> {
    return this.http.get<Page<ChangeOut>>(this.encodingUrl + '/' + encodingId + '/changes', { params: { page: page.toString(), size: size.toString() }, responseType: 'json', observe: 'body' });
  }
  createCapabilityToken(id: string ) :Observable<EncodingToken>{
    return this.http.put<EncodingToken>(this.encodingUrl + '/' + id + '/token', null, { responseType: 'json', observe: 'body' });
  }
  getEncodingByToken(token: string):Observable<EncodingPublicDetails> {
    return this.http.get<EncodingPublicDetails>(this.encodingUrl + '/' + token, {responseType: 'json', observe: 'body'});
  }
  getChangesByToken(token: string, page:number, size:number):Observable<Page<ChangeOut>> {
    return this.http.get<Page<ChangeOut>>(this.encodingUrl + '/token/' + token + '/changes', { params: { page: page.toString(), size: size.toString() }, responseType: 'json', observe: 'body' });
  }
  deleteCapabilityToken(id: string ):Observable<HttpResponse<any>> {
    return this.http.delete(this.encodingUrl + '/' + id + '/token', { observe: 'response' });
  }
  deleteEncoding(id: string):Observable<HttpResponse<any>> {
    return this.http.delete(this.encodingUrl + '/' + id, { observe: 'response' });
  }
  updateEncoding(id: string, encodingChanges: EncodingChanges):Observable<HttpResponse<any>> {
    const options = {
      noAttributesWithArrayNotation: true
    }

    const formData = serialize(encodingChanges, options);
    return this.http.patch(this.encodingUrl + '/' + id, formData, { observe: 'response' });
  }



}
