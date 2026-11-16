// Implement searchable, validated CRUD workflows for all five insurance resources.
import { Component, DestroyRef, inject, OnInit, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import {
  FormControl,
  FormGroup,
  FormRecord,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import { ActivatedRoute } from '@angular/router';

import { ApiService } from '../core/api.service';
import { errorMessage } from '../core/auth.service';
import { entityDefinition } from '../core/entity-definitions';
import { formatDate, formatMoney, toApiDate, toInputDate, todayInIstanbul } from '../core/formatters';
import {
  ApiRecord,
  ClaimPolicyContext,
  CustomerLookup,
  EntityDefinition,
  EntityField,
  ProductTypeRecord,
  ResourceKey
} from '../core/models';
import { crossFieldValidator, validatorsForField } from '../core/validators';

interface SearchableRecord extends ApiRecord {
  tckn_vkn?: string;
  first_name?: string;
  last_name?: string;
  email?: string | null;
  birth_date?: string | null;
  policy_id?: number;
  policy_no?: string | null;
  product_type?: string;
  start_date?: string;
  end_date?: string;
  premium_amount?: string;
  status?: string | null;
  claim_no?: string;
}

@Component({
  selector: 'kinsure-crud-page',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './crud-page.component.html',
  styleUrl: './crud-page.component.scss'
})
export class CrudPageComponent implements OnInit {
  private readonly api = inject(ApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly destroyRef = inject(DestroyRef);

  readonly loading = signal(false);
  readonly saving = signal(false);
  readonly error = signal('');
  readonly success = signal('');
  readonly records = signal<ApiRecord[]>([]);
  readonly editorOpen = signal(false);
  readonly editing = signal(false);
  readonly lookupOpen = signal(false);
  readonly pendingDelete = signal<ApiRecord | null>(null);
  readonly customerContext = signal<CustomerLookup | null>(null);
  readonly claimPolicyContext = signal<ClaimPolicyContext | null>(null);
  readonly productTypeOptions = signal<ReadonlyArray<{ value: string; label: string }>>([]);
  readonly lookupRecords = signal<SearchableRecord[]>([]);
  readonly lookupLoading = signal(false);
  readonly lookupError = signal('');
  readonly customerQuery = signal('');
  readonly recordKey = signal<string | number | null>(null);
  readonly offset = signal(0);
  readonly pageSize = 50;

  definition: EntityDefinition = entityDefinition('customers');
  fields: EntityField[] = [...this.definition.fields];
  searchFields = [...this.definition.searchFields];
  readonly form = new FormRecord<FormControl<string | boolean>>({});
  readonly searchForm = new FormRecord<FormControl<string>>({});
  readonly policyLookupForm = new FormGroup({
    tckn_vkn: new FormControl('', { nonNullable: true }),
    product_type: new FormControl('', { nonNullable: true }),
    start_date: new FormControl('', { nonNullable: true }),
    end_date: new FormControl('', { nonNullable: true }),
    status: new FormControl('', { nonNullable: true })
  });
  readonly formatDate = formatDate;
  readonly formatMoney = formatMoney;
  readonly stringValue = String;

  ngOnInit(): void {
    this.route.paramMap.pipe(takeUntilDestroyed(this.destroyRef)).subscribe((params) => {
      const key = params.get('resource') as ResourceKey | null;
      if (!key || !['usersins', 'customers', 'product-types', 'policies', 'claims'].includes(key)) {
        return;
      }
      this.configure(key);
    });
  }

  get isPolicyPage(): boolean {
    return this.definition.key === 'policies';
  }

  get isClaimPage(): boolean {
    return this.definition.key === 'claims';
  }

  get dateToday(): string {
    return todayInIstanbul();
  }

  get canContinue(): boolean {
    return this.records().length === this.pageSize;
  }

  get currentRange(): string {
    if (this.records().length === 0) {
      return '0 kayıt';
    }
    return `${this.offset() + 1}–${this.offset() + this.records().length} kayıt`;
  }

  configure(key: ResourceKey): void {
    this.definition = entityDefinition(key);
    this.fields = this.definition.fields.map((field) => ({ ...field }));
    this.searchFields = this.definition.searchFields.map((field) => ({ ...field }));
    this.records.set([]);
    this.error.set('');
    this.success.set('');
    this.editorOpen.set(false);
    this.pendingDelete.set(null);
    this.customerContext.set(null);
    this.claimPolicyContext.set(null);
    Object.keys(this.form.controls).forEach((name) => this.form.removeControl(name));
    this.form.clearValidators();
    Object.keys(this.searchForm.controls).forEach((name) => this.searchForm.removeControl(name));

    this.fields.forEach((field) => {
      const initialValue = field.name === 'is_active'
        ? true
        : field.name === 'status'
          ? key === 'claims' ? 'OPEN' : 'ACTIVE'
          : '';
      this.form.addControl(
        field.name,
        new FormControl<string | boolean>(initialValue, {
          nonNullable: true,
          validators: validatorsForField(field)
        })
      );
    });
    this.form.addValidators(crossFieldValidator(this.definition));
    this.searchFields.forEach((field) => {
      this.searchForm.addControl(field.name, new FormControl('', { nonNullable: true }));
    });

    if (key === 'policies' || key === 'claims') {
      this.loadProductTypes();
    }
    this.search();
  }

  search(resetPage = true): void {
    if (resetPage) {
      this.offset.set(0);
    }
    this.error.set('');
    const filters: Record<string, string> = {
      limit: String(this.pageSize),
      offset: String(this.offset()),
      ...this.searchPayload()
    };
    this.loading.set(true);
    this.api.list(this.definition.key, filters).subscribe({
      next: (records) => {
        this.records.set(records);
        this.loading.set(false);
      },
      error: (error: unknown) => {
        this.error.set(errorMessage(error));
        this.loading.set(false);
      }
    });
  }

  clearSearch(): void {
    this.searchForm.reset();
    this.search();
  }

  previousPage(): void {
    if (this.offset() === 0) {
      return;
    }
    this.offset.update((value) => Math.max(0, value - this.pageSize));
    this.search(false);
  }

  nextPage(): void {
    if (!this.canContinue) {
      return;
    }
    this.offset.update((value) => value + this.pageSize);
    this.search(false);
  }

  openCreate(): void {
    this.editing.set(false);
    this.recordKey.set(null);
    this.editorOpen.set(true);
    this.error.set('');
    this.success.set('');
    this.customerContext.set(null);
    this.claimPolicyContext.set(null);
    this.resetForm();
    this.setPrimaryKeyState(false);
    const password = this.form.controls['password'];
    if (password) {
      password.addValidators([Validators.required, Validators.minLength(8)]);
      password.updateValueAndValidity();
    }
  }

  openEdit(record: ApiRecord): void {
    this.editing.set(true);
    const key = record[this.definition.primaryKey];
    this.recordKey.set(typeof key === 'string' || typeof key === 'number' ? key : null);
    this.editorOpen.set(true);
    this.error.set('');
    this.success.set('');
    this.customerContext.set(null);
    this.claimPolicyContext.set(null);
    this.resetForm();
    this.setPrimaryKeyState(true);

    this.fields.forEach((field) => {
      const value = record[field.name];
      if (value === undefined || value === null) {
        this.form.controls[field.name]?.setValue(field.type === 'checkbox' ? false : '');
      } else if (field.type === 'date') {
        this.form.controls[field.name]?.setValue(toInputDate(value));
      } else {
        this.form.controls[field.name]?.setValue(
          field.type === 'checkbox' ? Boolean(value) : String(value)
        );
      }
    });
    const password = this.form.controls['password'];
    if (password) {
      password.removeValidators(Validators.required);
      password.setValue('');
      password.updateValueAndValidity();
    }
    if (this.isPolicyPage && typeof record['tckn_vkn'] === 'string') {
      this.lookupCustomer(record['tckn_vkn']);
    }
    if (this.isClaimPage && Number.isFinite(Number(record['policy_id']))) {
      this.lookupPolicy(Number(record['policy_id']));
    }
  }

  closeEditor(): void {
    this.editorOpen.set(false);
    this.resetForm();
    this.customerContext.set(null);
    this.claimPolicyContext.set(null);
  }

  save(): void {
    this.error.set('');
    this.success.set('');
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.saving.set(true);
    const payload = this.buildPayload();
    const primaryKey = String(this.recordKey() ?? '');
    const request = this.editing()
      ? this.api.update(this.definition.key, primaryKey, payload)
      : this.api.create(this.definition.key, payload);
    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.editorOpen.set(false);
        this.success.set(this.editing()
          ? `${this.definition.singular} kaydı güncellendi.`
          : `${this.definition.singular} başarıyla oluşturuldu.`);
        this.search();
      },
      error: (error: unknown) => {
        this.error.set(errorMessage(error));
        this.saving.set(false);
      }
    });
  }

  requestDelete(record: ApiRecord): void {
    this.pendingDelete.set(record);
  }

  cancelDelete(): void {
    this.pendingDelete.set(null);
  }

  confirmDelete(): void {
    const record = this.pendingDelete();
    if (!record) {
      return;
    }
    const key = record[this.definition.primaryKey];
    this.api.delete(this.definition.key, String(key)).subscribe({
      next: () => {
        this.pendingDelete.set(null);
        this.success.set(`${this.definition.singular} kaydı silindi.`);
        this.search();
      },
      error: (error: unknown) => {
        this.pendingDelete.set(null);
        this.error.set(errorMessage(error));
      }
    });
  }

  field(name: string): EntityField {
    return this.fields.find((item) => item.name === name) ?? {
      name,
      label: name,
      type: 'text'
    };
  }

  control(name: string): FormControl<string | boolean> {
    return this.form.controls[name];
  }

  searchControl(name: string): FormControl<string> {
    return this.searchForm.controls[name];
  }

  policySearchControl(name: 'tckn_vkn' | 'product_type' | 'start_date' | 'end_date' | 'status'): FormControl<string> {
    return this.policyLookupForm.controls[name];
  }

  hasFieldError(name: string): boolean {
    const control = this.form.controls[name];
    return Boolean(control && control.invalid && (control.touched || control.dirty));
  }

  fieldError(name: string): string {
    const errors = this.form.controls[name]?.errors;
    if (!errors) {
      return '';
    }
    if (errors['required']) {
      return 'Bu alan zorunludur.';
    }
    if (errors['pattern'] && name === 'tckn_vkn') {
      return 'TCKN / VKN 11 rakamdan oluşmalıdır.';
    }
    if (errors['email']) {
      return 'Geçerli bir e-posta adresi girin.';
    }
    if (errors['minlength'] && name === 'password') {
      return 'Şifre en az 8 karakter olmalıdır.';
    }
    if (errors['maxlength']) {
      return `En fazla ${this.field(name).maxLength} karakter girebilirsiniz.`;
    }
    if (errors['min']) {
      return 'Negatif olmayan bir değer girin.';
    }
    return 'Alan değerini kontrol edin.';
  }

  displayValue(record: ApiRecord, column: EntityDefinition['columns'][number]): string {
    const value = record[column.name];
    if (value === null || value === undefined || value === '') {
      return '—';
    }
    if (column.format === 'date') {
      return formatDate(value);
    }
    if (column.format === 'money') {
      return `${formatMoney(value)} ₺`;
    }
    if (column.format === 'boolean') {
      return value ? 'Aktif' : 'Pasif';
    }
    if (column.name === 'role') {
      return value === 'ADMIN' ? 'Yönetici' : value === 'USER' ? 'Kullanıcı' : String(value);
    }
    return String(value);
  }

  primaryValue(record: ApiRecord): string {
    const value = record[this.definition.primaryKey];
    return value === undefined || value === null ? '' : String(value);
  }

  openCustomerSearch(): void {
    this.lookupError.set('');
    this.lookupRecords.set([]);
    this.customerQuery.set('');
    this.lookupOpen.set(true);
  }

  searchCustomers(): void {
    const query = this.customerQuery().trim();
    const filters: Record<string, string> = { limit: '100' };
    if (query) {
      if (/^[0-9]{11}$/.test(query)) {
        filters['tckn_vkn'] = query;
      } else {
        filters['name'] = query;
      }
    }
    this.lookupLoading.set(true);
    this.lookupError.set('');
    this.api.list<SearchableRecord>('customers', filters).subscribe({
      next: (records) => {
        this.lookupRecords.set(records);
        this.lookupLoading.set(false);
      },
      error: (error: unknown) => {
        this.lookupError.set(errorMessage(error));
        this.lookupLoading.set(false);
      }
    });
  }

  chooseCustomer(record: SearchableRecord): void {
    if (!record.tckn_vkn) {
      return;
    }
    this.form.controls['tckn_vkn'].setValue(record.tckn_vkn);
    this.lookupOpen.set(false);
    this.lookupCustomer(record.tckn_vkn);
  }

  lookupCustomer(value = String(this.form.getRawValue()['tckn_vkn'] ?? '').trim()): void {
    if (!value) {
      this.customerContext.set(null);
      this.lookupError.set('TCKN / VKN girin veya müşteri seçin.');
      return;
    }
    this.lookupLoading.set(true);
    this.lookupError.set('');
    this.api.lookupCustomer(value).subscribe({
      next: (customer) => {
        this.customerContext.set(customer);
        this.lookupLoading.set(false);
        if (!customer) {
          this.lookupError.set('Müşteri bulunamadı.');
        }
      },
      error: (error: unknown) => {
        this.customerContext.set(null);
        this.lookupError.set(errorMessage(error));
        this.lookupLoading.set(false);
      }
    });
  }

  openPolicySearch(): void {
    this.lookupError.set('');
    this.lookupRecords.set([]);
    this.policyLookupForm.reset();
    this.lookupOpen.set(true);
    this.searchPolicyLookup();
  }

  searchPolicyLookup(): void {
    const values: Record<string, string> = { limit: '100' };
    ['tckn_vkn', 'product_type', 'start_date', 'end_date', 'status'].forEach((name) => {
      const rawValue = String(this.policyLookupForm.getRawValue()[name as keyof typeof this.policyLookupForm.controls] ?? '').trim();
      if (rawValue) {
        values[name] = name === 'start_date' || name === 'end_date'
          ? toApiDate(rawValue)
          : rawValue;
      }
    });
    this.lookupLoading.set(true);
    this.lookupError.set('');
    this.api.list<SearchableRecord>('policies', values).subscribe({
      next: (records) => {
        this.lookupRecords.set(records);
        this.lookupLoading.set(false);
      },
      error: (error: unknown) => {
        this.lookupError.set(errorMessage(error));
        this.lookupLoading.set(false);
      }
    });
  }

  choosePolicy(record: SearchableRecord): void {
    const policyId = Number(record.policy_id);
    if (!Number.isInteger(policyId) || policyId < 1) {
      return;
    }
    this.form.controls['policy_id'].setValue(String(policyId));
    this.lookupOpen.set(false);
    this.lookupPolicy(policyId);
  }

  lookupPolicy(value = Number(this.form.getRawValue()['policy_id'] ?? 0)): void {
    if (!Number.isInteger(value) || value < 1) {
      this.claimPolicyContext.set(null);
      this.lookupError.set('Geçerli bir poliçe ID girin veya poliçe seçin.');
      return;
    }
    this.lookupLoading.set(true);
    this.lookupError.set('');
    this.api.claimPolicyContext<ClaimPolicyContext & ApiRecord>(value).subscribe({
      next: (context) => {
        this.claimPolicyContext.set(context);
        this.lookupLoading.set(false);
      },
      error: (error: unknown) => {
        this.claimPolicyContext.set(null);
        this.lookupError.set(errorMessage(error));
        this.lookupLoading.set(false);
      }
    });
  }

  closeLookup(): void {
    this.lookupOpen.set(false);
  }

  private loadProductTypes(): void {
    this.api.list<ProductTypeRecord & ApiRecord>('product-types', { limit: '200' }).subscribe({
      next: (products) => {
        const options = products.map((product) => ({
          value: product.product_type,
          label: `${product.product_type} · ${product.product_name}`
        }));
        this.productTypeOptions.set(options);
        this.fields = this.fields.map((field) =>
          field.name === 'product_type' ? { ...field, options } : field
        );
        this.searchFields = this.searchFields.map((field) =>
          field.name === 'product_type' ? { ...field, options } : field
        );
      },
      error: (error: unknown) => this.error.set(errorMessage(error))
    });
  }

  private searchPayload(): Record<string, string> {
    const values = this.searchForm.getRawValue();
    const filters: Record<string, string> = {};
    this.searchFields.forEach((field) => {
      const rawValue = values[field.name]?.trim();
      if (rawValue) {
        filters[field.name] = field.type === 'date' ? toApiDate(rawValue) : rawValue;
      }
    });
    return filters;
  }

  private resetForm(): void {
    this.form.reset();
    this.fields.forEach((field) => {
      const defaultValue = field.type === 'checkbox'
        ? true
        : field.name === 'status'
          ? this.definition.key === 'claims' ? 'OPEN' : 'ACTIVE'
          : '';
      this.form.controls[field.name]?.setValue(defaultValue);
    });
    this.form.markAsPristine();
    this.form.markAsUntouched();
    this.form.updateValueAndValidity();
    this.lookupError.set('');
  }

  private setPrimaryKeyState(isEditing: boolean): void {
    this.fields.forEach((field) => {
      const control = this.form.controls[field.name];
      if (!control) {
        return;
      }
      if (field.immutableOnEdit && isEditing) {
        control.disable({ emitEvent: false });
      } else {
        control.enable({ emitEvent: false });
      }
    });
  }

  private buildPayload(): ApiRecord {
    const values = this.form.getRawValue();
    const payload: ApiRecord = {};
    this.fields.forEach((field) => {
      if (field.immutableOnEdit && this.editing()) {
        return;
      }
      const rawValue = values[field.name];
      if (field.name === 'password' && this.editing() && rawValue === '') {
        return;
      }
      if (field.type === 'date') {
        payload[field.name] = rawValue ? toApiDate(String(rawValue)) : null;
      } else if (field.type === 'number') {
        if (rawValue === '' && !field.required) {
          payload[field.name] = null;
        } else if (field.name === 'policy_id') {
          payload[field.name] = Number(rawValue);
        } else {
          payload[field.name] = String(rawValue);
        }
      } else if (field.type === 'checkbox') {
        payload[field.name] = Boolean(rawValue);
      } else if (typeof rawValue === 'string') {
        const normalized = rawValue.trim();
        payload[field.name] = normalized === '' && !field.required ? null : normalized;
      }
    });
    return payload;
  }
}
