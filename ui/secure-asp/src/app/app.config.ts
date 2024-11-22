import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter, RouterModule, withComponentInputBinding } from '@angular/router';

import { routes } from './app.routes';
import {HTTP_INTERCEPTORS, provideHttpClient, withInterceptorsFromDi} from "@angular/common/http";
import {TokenInterceptor} from "./interceptors/token/token.interceptor";
import {AuthGuard} from "./guards/auth/auth.guard";
import {NoAuthGuard} from "./guards/no-auth/no-auth.guard";
import { adminAuthGuard } from './guards/admin-auth/admin-auth.guard';
import { userAuthGuard } from './guards/user-auth/user-auth.guard';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes, withComponentInputBinding()),
    provideHttpClient(
      withInterceptorsFromDi()
    ),
    { provide: HTTP_INTERCEPTORS, useClass: TokenInterceptor, multi: true },
    AuthGuard, NoAuthGuard, adminAuthGuard, userAuthGuard,
  ]
};
