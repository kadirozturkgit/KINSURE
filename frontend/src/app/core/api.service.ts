// Provide the authenticated, same-origin API client used by all application screens.
import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiRecord, CustomerLookup, ResourceKey, TokenResponse } from './models';

const API_ROOT = '/api/v1';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);

  login(username: string, password: string): Observable<TokenResponse> {
    const body = new URLSearchParams({ username, password });
    return this.http.post<TokenResponse>(`${API_ROOT}/auth/login`, body.toString(), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
  }

  register<T>(payload: ApiRecord): Observable<T> {
    return this.http.post<T>(`${API_ROOT}/auth/register`, payload);
  }

  lookupCustomer(tcknVkn: string): Observable<CustomerLookup> {
    return this.http.get<CustomerLookup>(
      `${API_ROOT}/customers/lookup/${encodeURIComponent(tcknVkn)}`
    );
  }

  list<T extends ApiRecord>(
    resource: ResourceKey,
    filters: Record<string, string> = {}
  ): Observable<T[]> {
    let params = new HttpParams();
    Object.entries(filters).forEach(([key, value]) => {
      params = params.set(key, value);
    });
    return this.http.get<T[]>(`${API_ROOT}/${resource}`, { params });
  }

  get<T extends ApiRecord>(resource: ResourceKey, key: string | number): Observable<T> {
    return this.http.get<T>(`${API_ROOT}/${resource}/${encodeURIComponent(String(key))}`);
  }

  create<T extends ApiRecord>(resource: ResourceKey, payload: ApiRecord): Observable<T> {
    return this.http.post<T>(`${API_ROOT}/${resource}`, payload);
  }

  update<T extends ApiRecord>(
    resource: ResourceKey,
    key: string | number,
    payload: ApiRecord
  ): Observable<T> {
    return this.http.put<T>(`${API_ROOT}/${resource}/${encodeURIComponent(String(key))}`, payload);
  }

  delete(resource: ResourceKey, key: string | number): Observable<void> {
    return this.http.delete<void>(`${API_ROOT}/${resource}/${encodeURIComponent(String(key))}`);
  }

  claimPolicyContext<T extends ApiRecord>(policyId: number): Observable<T> {
    return this.http.get<T>(`${API_ROOT}/claims/policy/${policyId}`);
  }
}
