import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EncodingsComponent } from './encodings.component';

describe('EncodingsComponent', () => {
  let component: EncodingsComponent;
  let fixture: ComponentFixture<EncodingsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EncodingsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EncodingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
