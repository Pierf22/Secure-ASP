import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SigningFilesComponent } from './signing-files.component';

describe('SigningFilesComponent', () => {
  let component: SigningFilesComponent;
  let fixture: ComponentFixture<SigningFilesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SigningFilesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SigningFilesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
