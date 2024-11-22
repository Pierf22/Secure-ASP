import { Component, ElementRef, inject, NgModule, ViewChild } from '@angular/core';
import { NgbActiveModal, NgbNavModule, NgbProgressbarModule, NgbTypeahead } from '@ng-bootstrap/ng-bootstrap';
import { AlertService } from '../../services/alert/alert.service';
import { AbstractControl, FormArray, FormBuilder, FormGroup, FormsModule, NgModel, ReactiveFormsModule, Validators } from '@angular/forms';
import { ValidationService } from '../../services/validation/validation.service';
import { NgClass, NgForOf, NgIf } from '@angular/common';
import { catchError, debounceTime, distinctUntilChanged, map, Observable, of, OperatorFunction, switchMap } from 'rxjs';
import { UserService } from '../../services/user/user.service';
import { EncodingService } from '../../services/encoding/encoding.service';
import { Tag } from '../../models/tag';
import { Encoding } from '../../models/encoding';
import { AuthService } from '../../services/auth/auth.service';



@Component({
  selector: 'app-new-encodings-modal',
  standalone: true,
  imports: [NgbNavModule,NgbProgressbarModule, ReactiveFormsModule, NgIf, NgClass, FormsModule, NgbTypeahead, NgForOf],
  templateUrl: './new-encodings-modal.component.html',
  styleUrl: './new-encodings-modal.component.css'
})
export class NewEncodingsModalComponent {

  constructor(private authService:AuthService,  private alert:AlertService, private fb:FormBuilder, private validationService:ValidationService, private userService:UserService, private encodingService:EncodingService) {
    this.form = this.fb.group({
      name: ['', this.validationService.getNameValidator()],
      description: ['', Validators.compose([Validators.required, Validators.minLength(10)])],
      isPublic: [false, Validators.required],
      tags: this.fb.array([]),
      encoding: [null, Validators.compose([Validators.required])],
      signature: [null, Validators.compose([Validators.required])],
      collaborators:this.fb.array([]),
    });
  }
  modelTeam: any;
  modelTags: any;
	activeModal = inject(NgbActiveModal);
  form:FormGroup;
  active = 25;
  selectedOwnership: string = "SHARED";
  button50Clicked = false;
  button75Clicked = false;
  isGeneralInfoError() {
    return (( this.form.get('name')?.invalid) ||
    (this.form.get('description')?.invalid) )
     && this.active !== 25;
 }
 isFileError() {
  return (( this.form.get('encoding')?.invalid) && this.active !== 50 && this.button50Clicked);
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



firstClickTeams() {
  if(this.button75Clicked)
      return;
  this.button50Clicked = true;

}
addAUser(input: HTMLInputElement) {
  if(this.getCollaboratorsArray().length >= 20){
    this.alert.errorToast('You can add up to 20 collaborators');
    return;
  }
  this.getCollaboratorsArray().push(this.generateANewUser(input.value, this.selectedOwnership));
  input.value = '';
  this.selectedOwnership = "SHARED";
  this.alert.successToast('User added successfully');

  
  }
  generateANewUser(username: string, selectedOwnership: string): any {
    return this.fb.group({
      username: [username, Validators.required],
      ownership: [selectedOwnership, Validators.required]
    });
  }
  getCollaboratorsArray() {
    return this.form.get('collaborators') as FormArray;
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
                if (error.status === 401 || error.status === 403) {  // Handle unauthorized or forbidden errors
                  this.activeModal.dismiss();                          // Close the modal
                }
                return of([]);                                       // Return an empty array in case of an error
              })
            )
      )
    );
  
  
    

    deleteUser(index:number) {
      this.getCollaboratorsArray().removeAt(index);
      this.alert.successToast('User removed successfully');
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
                    if (error.status === 401 || error.status === 403) {  // Handle unauthorized or forbidden errors
                      this.activeModal.dismiss();                          // Close the modal
                    }
                    return of([]);                                       // Return an empty array in case of an error
                  })
                )
          )
        );


        addATag(input: HTMLInputElement) {
          if(this.getTagArray().length >= 10){
            this.alert.errorToast('You can add up to 10 tags');
            return;
          }
          this.getTagArray().push(this.generateANewTag(input.value));
          input.value = '';
          this.alert.successToast('Tag added successfully');
        
          }
  generateANewTag(value: string): any {
    return this.fb.group({
      name: [value, Validators.required]
    });
  }
  getTagArray() {
    return this.form.get('tags') as FormArray;
  }
  deleteTag(index: number) {
    this.getTagArray().removeAt(index);
    this.alert.successToast('Tag removed successfully');
    }
    userAlreadyAdd(): boolean {
      const user= this.modelTeam;
      for(let i=0; i<this.getCollaboratorsArray().length; i++){
        if(this.getCollaboratorsArray().at(i).value.username === user){
          return true;
        }
      }return false;
      }
      tagAlreadyAdd(): boolean {
        const tag= this.modelTags;
        for(let i=0; i<this.getTagArray().length; i++){
          if(this.getTagArray().at(i).value.name === tag){
            return true;
          }
        }return false;
        }


        saveEncoding() {
          this.alert.showSpinner();
          const name = this.form.get('name')?.value;
          const description = this.form.get('description')?.value;
          const isPublic = this.form.get('isPublic')?.value;
          const encoding = this.form.get('encoding')?.value;
          const signature = this.form.get('signature')?.value;
          let team:string[]=[];
          let ownership:string[]=[];
          let o
          for(let i=0; i<this.getCollaboratorsArray().length; i++){
            team.push(this.getCollaboratorsArray().at(i).value.username);
            ownership.push(this.getCollaboratorsArray().at(i).value.ownership);
          }
          let tags:string[] = [];
          for(let i=0; i<this.getTagArray().length; i++){
            tags.push(this.getTagArray().at(i).value.name);
          }
          const userId = this.authService.getUserId();
          if(name==null || description==null || isPublic==null || encoding==null || signature==null || userId==null){
            this.alert.errorToast('Please fill all the fields');
            return;
          }
          const encodingToSave:Encoding = new Encoding(name, description, isPublic, encoding, signature, team, tags, ownership);
          this.userService.saveEncoding(userId, encodingToSave).subscribe(
            data => {
              this.alert.successToast('Encoding saved successfully');
              this.activeModal.close();
            },
            error => {
              if(error.status === 401 || error.status === 403){
                this.activeModal.dismiss();
              }
              if(error.status===409){
                this.alert.errorToast('You already have an encoding with the same name');
                return

              }
              this.alert.errorToast('Error saving encoding');
            }
          );

        }
          
      
}
