export interface CertificationRequest{
  id:string;
  type:string;
  status:string;
  denied_reason:string | null;
  front_url:string;
  back_url:string;



  }

export interface CertificationRequestCount {
    pending: number;
    approved: number;
    rejected: number;
  
}
export class CertificationEdit {
  status: string;
  denied_reason: string | null;
  constructor(status: string, denied_reason: string|null) {
    this.status = status;
    this.denied_reason = denied_reason;
  }
}
export class CertificationRequestSave {
  front:File;
  back:File;
  type:string;
  constructor(front:File, back:File, type:string) {
    this.front = front;
    this.back = back;
    this.type = type;
  }
}





