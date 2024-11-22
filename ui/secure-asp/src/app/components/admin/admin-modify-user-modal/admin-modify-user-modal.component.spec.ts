import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminModifyUserModalComponent } from './admin-modify-user-modal.component';

describe('AdminModifyUserModalComponent', () => {
  let component: AdminModifyUserModalComponent;
  let fixture: ComponentFixture<AdminModifyUserModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminModifyUserModalComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdminModifyUserModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
