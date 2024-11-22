import { Component, inject, TemplateRef } from '@angular/core';
import { NgIf, NgClass, NgForOf } from '@angular/common';
import { ReactiveFormsModule, FormsModule, FormGroup, FormBuilder, FormArray } from '@angular/forms';
import { NgbCalendar, NgbDate, NgbDateParserFormatter, NgbDatepickerModule, NgbDateStruct, NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { NgbAccordionModule } from '@ng-bootstrap/ng-bootstrap';
import { NgbPagination } from '@ng-bootstrap/ng-bootstrap';
import { CertificationRequestDetailsComponent } from '../certification-request-details/certification-request-details.component';
import { Order, Page } from '../../models/page';
import { UserEncodingOut } from '../../models/user-encoding';
import { AuthService } from '../../services/auth/auth.service';
import { AlertService } from '../../services/alert/alert.service';
import { UserService } from '../../services/user/user.service';
import { Router } from '@angular/router';
import { TagService } from '../../services/tag/tag.service';
import { Ownership } from '../../models/ownership';
import { NewEncodingsModalComponent } from '../new-encodings-modal/new-encodings-modal.component';
import { EncodingOut } from '../../models/encoding';


@Component({
  selector: 'app-encodings',
  standalone: true,
  imports: [NgIf,
    NgClass,
    ReactiveFormsModule,
    NgForOf,
    CertificationRequestDetailsComponent,
    NgbDatepickerModule,
    FormsModule,
    NgbAccordionModule,
    NgbPagination],
  templateUrl: './encodings.component.html',
  styleUrl: './encodings.component.css'
})
export class EncodingsComponent {

  getTagColor(arg0: string): string {
    return this.tagService.getTagColor(arg0);
    }
    
      hoveredTag: number | null = null;  // 
      colorIndex: number = 0;
    
    getOwnerShipEnum() {
    return Ownership;
    }
    
      sort:string="";
      encodings:Page<UserEncodingOut> = {items: [], total: 0, page: 0, size: 0, pages: 0};
      order: Order = Order.ASC;
      calendar = inject(NgbCalendar);
      formatter = inject(NgbDateParserFormatter);
      hoveredDate: NgbDate | null = null;
      fromDate: NgbDate | null = null;
      toDate: NgbDate | null = null;
      today: NgbDate= this.calendar.getToday();
      searchForm:FormGroup;
      pageSize: number = 15;
    
    
    
    
      constructor(private fb:FormBuilder, protected authService: AuthService, private alert:AlertService, private modal:NgbModal, private userService:UserService, protected router:Router, private tagService:TagService) {
         this.searchForm = this.fb.group({
            name: [null ],
        dataBegin: [null],
        dataEnd: [null],
            tags: this.fb.array([]),
          });
        this.fetchEncodings(1, this.pageSize, this.sort, this.order);
      }
    
      ngOnInit(): void {
      this.searchForm.valueChanges.subscribe(() => {
        this.fetchEncodings(1, this.pageSize, this.sort, this.order);
      });
    
      }
    
    
    
      isHovered(date: NgbDate) {
        return (
          this.fromDate && !this.toDate && this.hoveredDate && date.after(this.fromDate) && date.before(this.hoveredDate)
        );
      }
    
      isInside(date: NgbDate) {
        return this.toDate && date.after(this.fromDate) && date.before(this.toDate);
      }
    
      isRange(date: NgbDate) {
        return (
          date.equals(this.fromDate) ||
          (this.toDate && date.equals(this.toDate)) ||
          this.isInside(date) ||
          this.isHovered(date)
        );
      }
      validateInput(currentValue: NgbDate | null, input: string): NgbDate | null {
        const parsed = this.formatter.parse(input);
        return parsed && this.calendar.isValid(NgbDate.from(parsed)) ? NgbDate.from(parsed) : currentValue;
      }
      onDateSelection(date: NgbDate) {
        if (!this.fromDate && !this.toDate) {
          this.fromDate = date;
        } else if (this.fromDate && !this.toDate && date && date.after(this.fromDate)) {
          this.toDate = date;
          this.searchForm.get('dataBegin')?.setValue(this.format(this.fromDate));
          this.searchForm.get('dataEnd')?.setValue(this.format(date));
        } else {
          this.toDate = null;
          this.searchForm.get('dataEnd')?.setValue(null);
          this.searchForm.get('dataBegin')?.setValue(null);
          this.fromDate = date;
        }
      }
      readonly DELIMITER = '/';
      format(date: NgbDateStruct | null): string {
        return date ? date.day + this.DELIMITER + date.month + this.DELIMITER + date.year  + "   -   "+this.fromDate?.day + this.DELIMITER + this.fromDate?.month + this.DELIMITER + this.fromDate?.year : '' ;
      }
    
      ascSort(parameter: string):boolean {
        return this.sort === parameter && this.order === Order.ASC;
        }
        descSort(parameter: string):boolean {
        return this.sort === parameter && this.order === Order.DESC;
        }
        changeOrder() {
        if(this.sort === '') {
          this.order = Order.ASC;
          return this.order;
        }else if(this.order === Order.ASC) {
          this.order = Order.DESC;
          return this.order;
        }else {
        this.order = Order.ASC;
        return this.order;
        }
      }
      changeSort(parameter: string) { 
        this.sort = parameter;
        return this.sort;
      }
    
      protected fetchEncodings(page: number, size: number, sort: string, order: Order) {
        this.alert.showSpinner();
        const userId= this.authService.getUserId();
        const name= this.searchForm.get('name')?.value;
        const fromUploadDate= this.fromDate ? new Date(this.fromDate.year, this.fromDate.month-1, this.fromDate.day+1) : undefined;
        const toUploadDate= this.toDate ? new Date(this.toDate.year, this.toDate.month-1, this.toDate.day+1) : undefined;
        let tags: string[] = [];
        for (let tag of this.searchForm.get('tags')?.value) {
          tags.push(tag.name);
        }
    
        if(!userId){
          this.alert.hideSpinner();
          return;}
        this.userService.getEncodings(userId, page, size, sort, order, name, tags, fromUploadDate, toUploadDate).subscribe(
          (response) => {
            this.encodings= response;
            this.alert.hideSpinner();
          },
          (error) => {
            this.alert.hideSpinner();
            if(error.status === 401 || error.status === 403) {
              return;}
            this.alert.errorToast("Error fetching encodings");
          }
        );
      }
    
    
    
      openModalNewEncoding() {
        const modalRef= this.modal.open(NewEncodingsModalComponent, {size: 'xl'});
        modalRef.result.then(
          (result) => {
            this.alert.successToast("Encoding upload completed");
            this.fetchEncodings(1, this.pageSize, this.sort, this.order);
          },
          (reason) => {
            
          },
        );
        }
    
        addTag(tag: HTMLInputElement) {
          const name = tag.value;
          if (!name)
          return; 
          tag.value = '';
          this.getTagArray().push(this.generateNewTagForm(name));
          
          }
          getTagArray(): FormArray {
            return this.searchForm.get('tags') as FormArray;
          }
          generateNewTagForm(name: string): FormGroup {
            return this.fb.group({
              name: [name],
            });
          }
          deleteTag(index: number) {
            this.getTagArray().removeAt(index);
          }
          openEncodingInfo(encoding: EncodingOut) {
          
            this.router.navigate([`/${encoding.owner_username}/${encoding.name}`]);
          }

          openNoSignedCert(_t12: TemplateRef<any>) {
            this.modal.open(_t12, {size: 'lg'});
          
          }
          navigateToProfile(modal:any) {
            this.router.navigate(['/profile'], { queryParams: { start: 'certification' } });
            modal.close();
          }
          
}
