// Manage the browser session and the authenticated user identity.
import { HttpErrorResponse } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

import { ApiService } from './api.service';
import { AuthUser, TokenResponse } from './models';

const TOKEN_KEY = 'kinsure.accessToken';
const USERNAME_KEY = 'kinsure.username';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly api = inject(ApiService);
  private readonly storedUsername = sessionStorage.getItem(USERNAME_KEY) ?? '';
  readonly token = signal<string | null>(sessionStorage.getItem(TOKEN_KEY));
  readonly username = signal<string>(this.storedUsername);

  login(username: string, password: string): Observable<TokenResponse> {
    return this.api.login(username, password).pipe(
      tap((response) => {
        sessionStorage.setItem(TOKEN_KEY, response.access_token);
        sessionStorage.setItem(USERNAME_KEY, username);
        this.token.set(response.access_token);
        this.username.set(username);
      })
    );
  }

  register(payload: Record<string, unknown>): Observable<AuthUser> {
    return this.api.register<AuthUser>(payload);
  }

  logout(): void {
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(USERNAME_KEY);
    this.token.set(null);
    this.username.set('');
  }
}

export function errorMessage(error: unknown): string {
  if (error instanceof HttpErrorResponse) {
    if (error.status === 0) {
      return 'Sunucuya bağlanılamadı. API adresini ve bağlantıyı kontrol edin.';
    }
    const body = error.error as { detail?: unknown } | null;
    if (typeof body?.detail === 'string') {
      return body.detail;
    }
    if (Array.isArray(body?.detail)) {
      return 'Gönderilen bilgileri kontrol edip yeniden deneyin.';
    }
    if (Array.isArray((body as { errors?: unknown[] } | null)?.errors)) {
      return 'Gönderilen bilgileri kontrol edip yeniden deneyin.';
    }
  }
  return 'İşlem tamamlanamadı. Lütfen yeniden deneyin.';
}
