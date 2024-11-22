import { Component, inject, Input, NgModule, OnInit, TemplateRef } from '@angular/core';
import { EncodingChanges, EncodingPublicDetails } from '../../models/encoding';
import { FormArray, FormBuilder, FormGroup, FormsModule, NgModel, ReactiveFormsModule, Validators } from '@angular/forms';
import { ValidationService } from '../../services/validation/validation.service';
import { UserEncodingPublicDetails } from '../../models/user-encoding';
import { NgClass, NgForOf, NgIf } from '@angular/common';
import { NgbAccordionModule, NgbModal, NgbNavModule, NgbTypeahead } from '@ng-bootstrap/ng-bootstrap';
import { AlertService } from '../../services/alert/alert.service';
import { catchError, debounceTime, distinctUntilChanged, map, Observable, of, OperatorFunction, switchMap } from 'rxjs';
import { EncodingService } from '../../services/encoding/encoding.service';
import { UserService } from '../../services/user/user.service';
import { AuthService } from '../../services/auth/auth.service';
import { environment } from '../../../enviroment/enviroment';
import { Router } from '@angular/router';

@Component({
  selector: 'app-encoding-settings',
  standalone: true,
  imports: [ReactiveFormsModule, NgClass, NgIf, NgbNavModule, NgForOf, FormsModule, NgbTypeahead, NgbAccordionModule],
  templateUrl: './encoding-settings.component.html',
  styleUrl: './encoding-settings.component.css'
})
export class EncodingSettingsComponent  implements OnInit{



@Input() encoding: EncodingPublicDetails|undefined;
form:FormGroup;
active = 'data';
hideLink = true;
modelTeam: any;
modelTags: any;
private modalService = inject(NgbModal);
constructor(private fb:FormBuilder, private validator:ValidationService, private alert:AlertService, private encodingService:EncodingService, private userService:UserService, private authService:AuthService, private router:Router) {
  this.form = this.fb.group({
    name : this.fb.control('', this.validator.getNameValidator()),
    description: ['', Validators.compose([Validators.required, Validators.minLength(10)])],
    isPublic: [false, Validators.required],
    tags: this.fb.array([]),
    encoding: [null ],
    signature: [null],
    collaborators:this.fb.array([]), //change if only you are owner
  });
 }
  ngOnInit(): void {
    if (this.encoding) {
      if(this.encoding.capability_token){
        this.hideLink = false;
      }
      this.form.patchValue({
      name: this.encoding.name,
      description: this.encoding.description,
      isPublic: this.encoding.is_public,
      });
      for (let tag of this.encoding.tags) {
        this.getTagsArray().push(this.generateANewTag(tag.name));
      }
      for (let collaborator of this.encoding.user_encodings) {

        this.getCollaboratorsArray().push(this.generateANewCollaborator(collaborator.user.username, collaborator.ownership.toString()));
      }
    }
  }
  isOwner(): boolean {
    for(let i=0; i<this.getCollaboratorsArray().length; i++){
      if(this.getCollaboratorsArray().at(i).value.username === this.authService.getUsername() && this.getCollaboratorsArray().at(i).value.ownership === 'Owner'){
        return true;
      }
    }return false;
  }
  generateANewCollaborator(collaborator: string, ownership:string): any {
    return this.fb.group({
      username: [collaborator, Validators.required],
      ownership: [ownership, Validators.required]
    });
  }
  getCollaboratorsArray() {
    return this.form.get('collaborators') as FormArray;
  }
  getTagsArray() {
    return this.form.get('tags') as FormArray;
  }

  addAUser(input: HTMLInputElement) {
    if(this.getCollaboratorsArray().length >= 20){
      this.alert.errorToast('You can add up to 20 collaborators');
      return;
    }
    this.getCollaboratorsArray().push(this.generateANewCollaborator(input.value, 'Shared'));
    input.value = '';
    this.alert.successToast('User added successfully');
  
    
    }

    userAlreadyAdd(): boolean {
      const user= this.modelTeam;
      for(let i=0; i<this.getCollaboratorsArray().length; i++){
        if(this.getCollaboratorsArray().at(i).value.username === user){
          return true;
        }
      }return false;
      }
      searchUser: OperatorFunction<string, readonly string[]> = (text$: Observable<string>) =>
        text$.pipe(
          debounceTime(100),              // Wait for 100ms after user stops typing
          distinctUntilChanged(),          // Ignore if the input is the same as the previous value
          switchMap((term) =>              // Switch to the new observable returned by the service
            term.length < 2
              ? of([])                     // If the input length is less than 2, return an empty array
              : this.userService.getUsernames(term).pipe(  // Call the service's getUsernames method
                  map((response) => response.items.map(user => user.username)),       // Map the result to the items from the Page<string>
                  catchError((error) => {
                    this.modelTeam = term;
                    return of([]);                                       // Return an empty array in case of an error
                  })
                )
          )
        );
  generateANewTag(value: string): any {
    return this.fb.group({
      name: [value, Validators.required]
    });
  }
  searchTag: OperatorFunction<string, readonly string[]> = (text$: Observable<string>) =>
    text$.pipe(
      debounceTime(100),              // Wait for 100ms after user stops typing
      distinctUntilChanged(),          // Ignore if the input is the same as the previous value
      switchMap((term) =>              // Switch to the new observable returned by the service
        term.length < 2
          ? of([])                     // If the input length is less than 2, return an empty array
          : this.encodingService.getTags(term).pipe(  // Call the service's getTags method
              map((response) => response.items.map(tag => tag.name)),       // Map the result to the items from the Page<string>
              catchError((error) => {
                this.modelTeam = term;
                
                return of([]);                                       // Return an empty array in case of an error
              })
            )
      )
    );


    addATag(input: HTMLInputElement) {
      if(this.getTagsArray().length >= 10){
        this.alert.errorToast('You can add up to 10 tags');
        return;
      }
      this.getTagsArray().push(this.generateANewTag(input.value));
      input.value = '';
      this.alert.successToast('Tag added successfully');
    
      }
      tagAlreadyAdd(): boolean {
        const tag= this.modelTags;
        for(let i=0; i<this.getTagsArray().length; i++){
          if(this.getTagsArray().at(i).value.name === tag){
            return true;
          }
        }return false;
        }
        deleteTag(index: number) {
          this.getTagsArray().removeAt(index);
          this.alert.successToast('Tag removed successfully');
          }
          notChangeForm(): boolean {
            const option1= this.form.get('name')?.value === this.encoding?.name &&
            this.form.get('description')?.value === this.encoding?.description &&
            this.form.get('isPublic')?.value === this.encoding?.is_public && 
            this.form.get('encoding')?.value === null &&
            this.form.get('signature')?.value === null;
            if(!this.encoding?.tags)
              return option1
            const formTagsArray = this.getTagsArray().controls.map(control => control.value.name);
            const formTeamsArray = this.getCollaboratorsArray().controls.map(control => control.value.username);
            const savedTagsArray = this.encoding?.tags.map(tag => tag.name);
            const savedTeamsArray = this.encoding?.user_encodings.map(user => user.user);
            if (formTeamsArray.length !== savedTeamsArray.length) {
              return false;
            }

            if (formTagsArray.length !== savedTagsArray.length) {
              return false;
            }
            const tagsAreEqual = formTagsArray.every(tag => savedTagsArray.includes(tag));
            const teamsAreEqual = formTeamsArray.every(team => savedTeamsArray.includes(team));
            return option1 && tagsAreEqual && teamsAreEqual;
          }
            saveChangesData() {
            throw new Error('Method not implemented.');
            }
            saveFile($event: Event) {
              // Get the first file from the input
              let file = ($event.target as HTMLInputElement).files?.item(0);
              
              // Define the maximum file size (100MB)
              const max_size = 100 * 1024 * 1024; // 100 MB
              
              // Allowed file extensions: .asp, .txt, or no extension
              const allowedExtensions = ['asp', 'txt', '']; // '' represents files with no extension
            
              if (file) {
                // Check if the file size exceeds the maximum allowed size
                if (file.size > max_size) {
                  // If file size exceeds 100MB, set a 'max_size' error on the form control
                  this.form.get('encoding')?.setErrors({ 'max_size': true });
                  return;
                }
            
                // Extract the file name and extension
                let fileName = file.name;
                
                // Check if the file has an extension. If not, assign an empty string to represent no extension
                let fileExtension = fileName.includes('.') ? fileName.split('.').pop() : ''; 
            
                // Validate the file extension: must be either .asp, .txt, or no extension
                if (!allowedExtensions.includes(fileExtension?.toLowerCase() || '')) {
                  // If the extension is invalid, set an 'invalid_extension' error on the form control
                  this.form.get('encoding')?.setErrors({ 'invalid_extension': true });
                  return;
                }
            
                // If the file passes both size and extension checks, clear any previous errors
                this.form.get('encoding')?.setErrors(null);
                
                // Patch the file into the form control (ignoring TypeScript warnings about type mismatch)
                // @ts-ignore
                this.form.patchValue({ encoding: file });
              }}
              saveFileSignature($event: Event) {
                // Get the first file from the input
                let file = ($event.target as HTMLInputElement).files?.item(0);
                
             // Define the maximum file size (1MB)
            const max_size = 1 * 1024 * 1024; // 1 MB
            
                
                // Allowed file extensions: .bin, .sign, or sig extension
                const allowedExtensions = ['bin', 'sign', 'sig', 'sha256']; // '' represents files with no extension
              
                if (file) {
                  // Check if the file size exceeds the maximum allowed size
                  if (file.size > max_size) {
                    // If file size exceeds 1MB, set a 'max_size' error on the form control
                    this.form.get('signature')?.setErrors({ 'max_size': true });
                    return;
                  }
              
                  // Extract the file name and extension
                  let fileName = file.name;
                  
                  // Check if the file has an extension. If not, assign an empty string to represent no extension
                  let fileExtension = fileName.includes('.') ? fileName.split('.').pop() : ''; 
              
                  // Validate the file extension: must be either .bin, .sig, or sign extension
                  if (!allowedExtensions.includes(fileExtension?.toLowerCase() || '')) {
                    // If the extension is invalid, set an 'invalid_extension' error on the form control
                    this.form.get('signature')?.setErrors({ 'invalid_extension': true });
                    return;
                  }
              
                  // If the file passes both size and extension checks, clear any previous errors
                  this.form.get('signature')?.setErrors(null);
                  
                  // Patch the file into the form control (ignoring TypeScript warnings about type mismatch)
                  // @ts-ignore
                  this.form.patchValue({ signature: file });
                }
            }
            
   

    deleteUser(index:number) {
      this.getCollaboratorsArray().removeAt(index);
      this.alert.successToast('User removed successfully');
      }
      createACapabilityUrl() {
        const id = this.encoding?.id;
        if(!id || !this.encoding){
          return;
        }
        this.alert.showSpinner();
        this.encodingService.createCapabilityToken(id).subscribe((response) => {
          this.encoding!.capability_token = response.token;
          this.hideLink = false;
          this.alert.successToast('Capability token created successfully');
        }, (error) => {
          this.alert.errorToast('Failed to create capability token');
        });
      }

isCurrentUser(arg0: any): boolean {
const user = this.authService.getUsername();
return user !== arg0;
}
copyToClipboard(arg0: string) {
const el = document.createElement('textarea');
el.value = arg0;
document.body.appendChild(el);
el.select();
document.execCommand('copy');
document.body.removeChild(el);
this.alert.successToast('Link copied to clipboard');

}
getUrl() {
return environment.frontendUrl+'/encodings/';
}
deleteSharingUrl() {
  if(!this.encoding){
    return;
  }
  this.alert.showSpinner();
  this.encodingService.deleteCapabilityToken(this.encoding?.id).subscribe(() => {
    this.encoding!.capability_token = null;
    this.hideLink = true;
    this.alert.successToast('Capability token deleted successfully');
  }, (error) => {
    this.alert.errorToast('Failed to delete capability token');
  });
  }

  openConfirmationModal(content: TemplateRef<any>) {
    this.modalService.open(content, { ariaLabelledBy: 'modal-delete-confirmation' }).result.then(
			(result) => {
				this.deleteENcoding();
			},
			
		);
    }
    deleteENcoding() {
      if(!this.encoding){
        return;
      }
      this.alert.showSpinner();
      this.encodingService.deleteEncoding(this.encoding.id).subscribe(() => {
        this.router.navigate(['/encodings']).then(() => {this.alert.successToast('Encoding deleted successfully'); });
      }, (error) => {
        this.alert.errorToast('Failed to delete encoding');
      });
    }
    saveChangesEncoding() {
      if(!this.encoding){
        return;
      }
      this.alert.showSpinner();
      const encodingChanges = new EncodingChanges();
      if(this.form.get('name')?.value !== this.encoding.name){
        encodingChanges.name = this.form.get('name')?.value;
      }
      if(this.form.get('description')?.value !== this.encoding.description){
        encodingChanges.description = this.form.get('description')?.value;
      }
      if(this.form.get('isPublic')?.value !== this.encoding.is_public){
        encodingChanges.is_public = this.form.get('isPublic')?.value;
      }
      if(this.form.get('encoding')?.value!=null && this.form.get('signature')?.value!=null){
        encodingChanges.encoding_file = this.form.get('encoding')?.value;
        encodingChanges.signature_file = this.form.get('signature')?.value;
      }
      let tags:string[] = [];
      let teams:string[] = [];
      let ownerships:string[] = [];
      for(let i=0; i<this.getTagsArray().length; i++){
        tags.push(this.getTagsArray().at(i).value.name);
      }
      if(tags.length>0){
        encodingChanges.tags = tags;
      }
      for(let i=0; i<this.getCollaboratorsArray().length; i++){
        teams.push(this.getCollaboratorsArray().at(i).value.username);
        ownerships.push(this.getCollaboratorsArray().at(i).value.ownership.toString().toUpperCase());
      }
      if(teams.length>0){
        encodingChanges.teams = teams;
        encodingChanges.ownerships = ownerships;
      }
      this.encodingService.updateEncoding(this.encoding.id, encodingChanges).subscribe(() => {
        this.router.navigate(['/encodings']).then(() => {this.alert.successToast('Encoding changed successfully'); });
      }, (error) => {
        this.alert.errorToast('Failed to save changes');
      });

    
    
    
    
    
    
    }
}
