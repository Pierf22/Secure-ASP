import { Tag, TagName} from "./tag";
import { UserEncodingOut, UserEncodingPublicDetails } from "./user-encoding";

export class Encoding{
    name:string;
    description:string;
    is_public:boolean;
    encoding_file:File;
    signature_file:File;
    teams:string[];
    ownerships:string[];
    tags:string[];

    constructor(name:string, description:string, is_public:boolean, encoding:File, signature:File, teams:string[], tags:string[], ownerships:string[]){
        this.name = name;
        this.description = description;
        this.is_public = is_public;
        this.encoding_file = encoding;
        this.signature_file= signature;
        this.teams = teams;
        this.tags = tags;
        this.ownerships = ownerships;
    }

}
export interface EncodingOut{
    name:string;
    is_public:boolean;
    upload_date:Date;
    tags:TagName[];
    owner_username:string;
    
}
export interface EncodingPublic{
    name:string;
    description:string;
    tags:TagName[];

}
export interface EncodingPublicDetails{
    id:string;
    name:string;
    description:string;
    tags:Tag[];
    owner_username:string;
    is_public:boolean;
    upload_date:Date;
    file_url:string;
    user_encodings:UserEncodingPublicDetails[];
    capability_token:string|null;
}
export class EncodingChanges{
    name?:string;
    description?:string;
    is_public?:boolean;
    teams?:string[];
    ownerships?:string[];
    tags?:string[];
    encoding_file?:File
    signature_file?:File
    constructor(name?:string, description?:string, publicValue?:boolean, tags?:string[], encoding?:File, signature?:File, teams?:string[], ownerships?:string[]){
        this.name = name;
        this.description = description;
        this.is_public = publicValue;
        this.encoding_file = encoding;
        this.signature_file = signature;
        this.teams = teams;
        this.tags = tags;
        this.ownerships = ownerships;
    }
}
export interface EncodingCount{
    count: [number, number][];
}