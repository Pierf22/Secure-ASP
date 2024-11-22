import { EncodingPublic } from "./encoding";

export class UserRegister {
  email: string;
  password: string;
  username: string;
  full_name: string;

  constructor(email: string, password: string, username: string, full_name: string) {
    this.email = email;
    this.password = password;
    this.username = username;
    this.full_name = full_name;
  }

}
export class UserProfile {
  email: string;
  username: string;
  full_name: string;
  oauth2_user: boolean;

  constructor(data: any) {
    this.email = data.email;
    this.username = data.username;
    this.full_name = data.full_name;
    this.oauth2_user = data.oauth2_user;
  }

}
export class UserEdit {
  email: string | undefined;
  username: string | undefined;
  full_name: string | undefined;
  password: string | undefined;
  disabled: boolean | undefined;
  roles: string[] | undefined;

  constructor(email: string|undefined, username: string|undefined, full_name: string|undefined, password: string|undefined, disabled: boolean|undefined, roles: string[]|undefined) {
    this.email = email;
    this.username = username;
    this.full_name = full_name;
    this.password = password;
    this.disabled = disabled;
    this.roles = roles;
  }

}
export interface UserCount {
  total: number;
  disabled: number;
  active: number;
  oauth2: number;
  username_password: number;
}
export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  oauth2_user: boolean;
  disabled: boolean;
  roles: string[];
  certification_status: string|null;
}
export interface UserKeys {
  public_key: string;
  private_key: string;
  certificate: string;
}
export interface UserUsername {
  username: string;
}
export interface UserPublicProfile {
  full_name: string;
  username: string;

}