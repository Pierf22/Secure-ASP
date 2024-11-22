import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GeneratingCsrRequestComponent } from './generating-csr-request.component';

describe('GeneratingCsrRequestComponent', () => {
  let component: GeneratingCsrRequestComponent;
  let fixture: ComponentFixture<GeneratingCsrRequestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GeneratingCsrRequestComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GeneratingCsrRequestComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
