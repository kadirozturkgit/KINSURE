// Define public authentication routes and the authenticated application workspace.
import { Routes } from '@angular/router';

import { authGuard } from './core/auth.guard';
import { CrudPageComponent } from './pages/crud-page.component';
import { DashboardHomeComponent } from './pages/dashboard-home.component';
import { LoginComponent } from './pages/login.component';
import { WorkspaceComponent } from './pages/workspace.component';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'app' },
  { path: 'login', component: LoginComponent },
  {
    path: 'app',
    component: WorkspaceComponent,
    canActivate: [authGuard],
    children: [
      { path: '', component: DashboardHomeComponent },
      { path: ':resource', component: CrudPageComponent }
    ]
  },
  { path: '**', redirectTo: 'app' }
];
