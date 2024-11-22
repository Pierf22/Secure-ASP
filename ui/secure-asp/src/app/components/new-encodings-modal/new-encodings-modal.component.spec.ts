import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewEncodingsModalComponent } from './new-encodings-modal.component';

describe('NewEncodingsModalComponent', () => {
  let component: NewEncodingsModalComponent;
  let fixture: ComponentFixture<NewEncodingsModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewEncodingsModalComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NewEncodingsModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
