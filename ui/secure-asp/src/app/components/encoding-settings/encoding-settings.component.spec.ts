import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EncodingSettingsComponent } from './encoding-settings.component';

describe('EncodingSettingsComponent', () => {
  let component: EncodingSettingsComponent;
  let fixture: ComponentFixture<EncodingSettingsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EncodingSettingsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EncodingSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
