import { Injectable } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {environment} from "../../../enviroment/enviroment";
import { serialize } from 'object-to-formdata';
import {Observable} from "rxjs";
import { CertificationEdit, CertificationRequest, CertificationRequestCount, CertificationRequestSave } from '../../models/certification-request';

@Injectable({
  providedIn: 'root'
})
export class CertificationRequestService {
  editCertificationRequest(id: string, certification: CertificationEdit) {
    return this.http.put(environment.backendUrl+"/v1/certification-requests/"+id, certification);
  }


  constructor(private http:HttpClient) { }

  getCertificationRequest(userId:string): Observable<CertificationRequest> {
    return this.http.get<CertificationRequest>(environment.backendUrl+"/v1/users/"+userId+"/certification-request");
  }


  getDocumentTypes():Observable<string[]> {
    return this.http.get<string[]>(environment.backendUrl+"/v1/certification-requests/document-types", {observe: 'body', responseType: 'json'});
  }

  saveCertificationRequest(userId: string, certification:CertificationRequestSave) {
    const formData = serialize(certification);
    return this.http.post(environment.backendUrl+"/v1/users/"+userId+"/certification-request", formData);

  }
  getCertificationRequestsCount():Observable<CertificationRequestCount> {
    return this.http.get<CertificationRequestCount>(environment.backendUrl+"/v1/certification-requests/count", {observe: 'body', responseType: 'json'});
  }
  deleteCertificationRequest(certificationId: string) {
    return this.http.delete(environment.backendUrl+"/v1/certification-requests/"+certificationId, {observe: 'response'});
  }

  loadFile(url: string):Observable<Blob> {
    return this.http.get(url, {responseType: 'blob'});
  }
  getStatus(): Observable<string[]> {
    return this.http.get<string[]>(environment.backendUrl+"/v1/certification-requests/status", {observe: 'body', responseType: 'json'});
  }
}
