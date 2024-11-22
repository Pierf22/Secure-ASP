import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CertificationRequestDetailsComponent } from './certification-request-details.component';

describe('CertificationRequestDetailsComponent', () => {
  let component: CertificationRequestDetailsComponent;
  let fixture: ComponentFixture<CertificationRequestDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CertificationRequestDetailsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CertificationRequestDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
