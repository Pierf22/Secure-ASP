import { Routes, withComponentInputBinding } from '@angular/router';
import {HomeComponent} from "./components/home/home.component";
import {LoginComponent} from "./components/login/login.component";
import {SignUpComponent} from "./components/sign-up/sign-up.component";
import {DashboardComponent} from "./components/dashboard/dashboard.component";
import {AuthGuard} from "./guards/auth/auth.guard";
import {NoAuthGuard} from "./guards/no-auth/no-auth.guard";
import {ProfileComponent} from "./components/profile/profile.component";
import { AdminDashboardComponent } from './components/admin/admin-dashboard/admin-dashboard.component';
import { adminAuthGuard } from './guards/admin-auth/admin-auth.guard';
import { AdminUsersComponent } from './components/admin/admin-users/admin-users.component';
import { userAuthGuard } from './guards/user-auth/user-auth.guard';
import { PublicUserProfileComponent } from './components/public-user-profile/public-user-profile.component';
import { EncodingComponent } from './components/encoding/encoding.component';
import { EncodingsComponent } from './components/encodings/encodings.component';
import { GuidesComponent } from './components/guides/guides.component';
import { GeneratingKeyGuideComponent } from './components/guides/steps/generating-key-guide/generating-key-guide.component';
import { GeneratingCsrRequestComponent } from './components/guides/steps/generating-csr-request/generating-csr-request.component';
import { SigningFilesComponent } from './components/guides/steps/signing-files/signing-files.component';
import { UploadFilesComponent } from './components/guides/steps/upload-files/upload-files.component';
import { ViewingFilesComponent } from './components/guides/steps/viewing-files/viewing-files.component';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/home',
    pathMatch: 'full'
  },
  {
    path: 'profile',
    component: ProfileComponent,
    canActivate: [AuthGuard]
  }
  ,
  {
    path: 'home',
    component: HomeComponent,
    canActivate:[NoAuthGuard]

  },
  {
    path:'login',
    component: LoginComponent,
    canActivate:[NoAuthGuard]
  },
  {
    path:'sign-up',
    component: SignUpComponent,
    canActivate:[NoAuthGuard]
  },
 
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [userAuthGuard]
  },
  {
    path: "encodings",
    component:EncodingsComponent
  },
  {
    path: "encodings/:token",
    component:EncodingComponent
  },
  {
    path: 'dashboard/admin',
    component: AdminDashboardComponent,
    canActivate: [adminAuthGuard]
  },
   {
    path: "users",
    component:AdminUsersComponent,
    canActivate: [adminAuthGuard]
   },
   {
    path:"guides",
    component:GuidesComponent
   },
   {
    path: "guides/key-gen",
    component:GeneratingKeyGuideComponent
   },
   {
    path: "guides/csr-gen",
    component:GeneratingCsrRequestComponent
   },
   {
    path: "guides/file-sign",
    component:SigningFilesComponent,
   },
   {
    path: "guides/upload-files",
    component:UploadFilesComponent,
   },
   {
    path: "guides/file-view",
    component:ViewingFilesComponent,
   },
   {
    path: ":username",
    component: PublicUserProfileComponent,
   },
    {
      path: ":username/:encodingName",
      component:EncodingComponent
    }
];
