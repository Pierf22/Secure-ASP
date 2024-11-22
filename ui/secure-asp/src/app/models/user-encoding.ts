import { Ownership } from "./ownership";
import { EncodingOut, EncodingPublic } from "./encoding";
import { UserUsername } from "./user";
 


export interface UserEncodingOut {
    ownership: Ownership;
    encoding:EncodingOut;
}
export interface UserEncodingPublic {
    encoding:EncodingPublic;
}
export interface UserEncodingPublicDetails {
    ownership: Ownership;
    user:UserUsername;
}