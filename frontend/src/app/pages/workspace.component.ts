// Render the authenticated application shell and primary insurance navigation.
import { Component, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { AuthService } from '../core/auth.service';
import { ResourceKey } from '../core/models';

@Component({
  selector: 'kinsure-workspace',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './workspace.component.html',
  styleUrl: './workspace.component.scss'
})
export class WorkspaceComponent {
  private readonly router = inject(Router);
  readonly auth = inject(AuthService);
  readonly todayLabel = new Intl.DateTimeFormat('tr-TR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  }).format(new Date());

  readonly navigation: ReadonlyArray<{ key: ResourceKey; label: string; icon: string }> = [
    { key: 'usersins', label: 'Kullanıcılar', icon: '◉' },
    { key: 'customers', label: 'Müşteriler', icon: '◌' },
    { key: 'product-types', label: 'Ürün türleri', icon: '◈' },
    { key: 'policies', label: 'Poliçeler', icon: '▤' },
    { key: 'claims', label: 'Hasarlar', icon: '⌁' }
  ];

  logout(): void {
    this.auth.logout();
    void this.router.navigate(['/login']);
  }
}
