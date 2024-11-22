import { Component, inject, OnInit } from '@angular/core';
import { UserService } from '../../../services/user/user.service';
import {NgClass,  NgIf, NgFor} from "@angular/common";
import { User } from '../../../models/user';
import { Order, Page } from '../../../models/page';
import { NgbModal, NgbPagination } from '@ng-bootstrap/ng-bootstrap';
import { AlertService } from '../../../services/alert/alert.service';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { AdminModifyUserModalComponent } from '../admin-modify-user-modal/admin-modify-user-modal.component';

@Component({
  selector: 'app-admin-users',
  standalone: true,
  imports: [NgFor, NgClass, NgIf, NgbPagination, ReactiveFormsModule],
  templateUrl: './admin-users.component.html',
  styleUrl: './admin-users.component.css'
})
export class AdminUsersComponent implements OnInit {

  private modalService = inject(NgbModal);
  users:Page<User> = {items: [], total: 0, page: 0, size: 0, pages: 0};
  pageSize: number = 15
  sort: string = '';
  searchForm:FormGroup;
  order: Order = Order.ASC;
  constructor(private userService:UserService, private alertService:AlertService, private router:Router, private fb:FormBuilder) {
    this.searchForm = this.fb.group({
      username: [''],
      email: [''],
      fullName: [''],
    });
  }



  ngOnInit(): void {
    this.fetchUsers(1, this.pageSize, this.sort, this.order);
    this.searchForm.valueChanges.subscribe(() => {
      this.fetchUsers(1, this.pageSize, this.sort, this.order);
    });
}

    ascSort(parameter: string):boolean {
      return this.sort === parameter && this.order === Order.ASC;
    }
    descSort(parameter: string):boolean {
      return this.sort === parameter && this.order === Order.DESC;
    }
    noSort():boolean {
      return this.sort === '';
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
  getUserRoles(user: User) {
    let roles=[]
    if (this.isAdminAndUser(user)) {
      roles.push('User and Admin');
  } else if (this.isAdmin(user)) {
      roles.push('Admin');
  } else {
      roles.push('User');
  }

  return roles.join(', ');
      }
      isAdmin(user: User) {
        return user.roles.includes('ROLE_ADMIN');
      }
      isAdminAndUser(user: User) {
        return user.roles.includes('ROLE_ADMIN') && user.roles.includes('ROLE_USER');
      }



    fetchUsers(page: number, size: number, sort: string, order: Order) {
      const username = this.searchForm.get('username')?.value;
      const email = this.searchForm.get('email')?.value;
      const full_name = this.searchForm.get('fullName')?.value;
      this.userService.getUsers(page,size, sort, order, username, email, full_name).subscribe((data)=>{
        this.users=data;
      }, (error)=>{
        if(error.status == 401) {
          this.alertService.warning("Please login to access this page");
          return;
        }
        this.alertService.error("Failed to fetch users").then(() => {
          this.router.navigate(['/']);
        });
    });}
    openUserModifyModal(user: User) {
      const modalRef = this.modalService.open(AdminModifyUserModalComponent, {centered: true, size: 'xl', });
		modalRef.componentInstance.user = user;
    modalRef.result.then(
			(result) => {
				if (result) {
          this.fetchUsers(1, this.pageSize, this.sort, this.order);
        }
			},
			(ignored) => {
				
			},
		);
}
}
