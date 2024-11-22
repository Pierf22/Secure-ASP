import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewingFilesComponent } from './viewing-files.component';

describe('ViewingFilesComponent', () => {
  let component: ViewingFilesComponent;
  let fixture: ComponentFixture<ViewingFilesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ViewingFilesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ViewingFilesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
