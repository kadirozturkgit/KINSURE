// Load high-level record totals and shortcuts for the authenticated dashboard.
import { Component, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { ApiService } from '../core/api.service';
import { AuthService, errorMessage } from '../core/auth.service';
import { ResourceKey } from '../core/models';

@Component({
  selector: 'kinsure-dashboard-home',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './dashboard-home.component.html',
  styleUrl: './dashboard-home.component.scss'
})
export class DashboardHomeComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly auth = inject(AuthService);
  readonly username = this.auth.username();
  readonly todayLabel = new Intl.DateTimeFormat('tr-TR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    timeZone: 'Europe/Istanbul'
  }).format(new Date());
  readonly totals = signal<Record<ResourceKey, number>>({
    usersins: 0,
    customers: 0,
    'product-types': 0,
    policies: 0,
    claims: 0
  });
  readonly loading = signal(true);
  readonly error = signal('');

  readonly cards: ReadonlyArray<{ key: ResourceKey; label: string; hint: string; icon: string }> = [
    { key: 'customers', label: 'Müşteriler', hint: 'Müşteri kaydı', icon: '◌' },
    { key: 'policies', label: 'Poliçeler', hint: 'Aktif portföy', icon: '▤' },
    { key: 'claims', label: 'Hasarlar', hint: 'Hasar kaydı', icon: '⌁' },
    { key: 'product-types', label: 'Ürün türleri', hint: 'Tanımlı ürün', icon: '◈' }
  ];

  readonly quickLinks: ReadonlyArray<{ key: ResourceKey; label: string; description: string; icon: string }> = [
    { key: 'customers', label: 'Müşteri ekle', description: 'Yeni müşteri kaydı oluşturun', icon: '＋' },
    { key: 'policies', label: 'Poliçe oluştur', description: 'Yeni sigorta poliçesi ekleyin', icon: '▤' },
    { key: 'claims', label: 'Hasar bildirimi', description: 'Hasar kaydı oluşturun', icon: '⌁' }
  ];

  ngOnInit(): void {
    const resources: ResourceKey[] = ['usersins', 'customers', 'product-types', 'policies', 'claims'];
    let remaining = resources.length;
    const totals = { ...this.totals() };
    resources.forEach((resource) => {
      this.api.list(resource, { limit: '200' }).subscribe({
        next: (rows) => {
          totals[resource] = rows.length;
          this.finishLoad(--remaining, totals);
        },
        error: (error: unknown) => {
          this.error.set(errorMessage(error));
          this.finishError(--remaining, totals);
        }
      });
    });
  }

  private finishLoad(remaining: number, totals: Record<ResourceKey, number>): void {
    this.totals.set(totals);
    if (remaining === 0) {
      this.loading.set(false);
    }
  }

  private finishError(remaining: number, totals: Record<ResourceKey, number>): void {
    this.totals.set(totals);
    if (remaining === 0) {
      this.loading.set(false);
    }
  }
}
