import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GeneratingKeyGuideComponent } from './generating-key-guide.component';

describe('GeneratingKeyGuideComponent', () => {
  let component: GeneratingKeyGuideComponent;
  let fixture: ComponentFixture<GeneratingKeyGuideComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GeneratingKeyGuideComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GeneratingKeyGuideComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
