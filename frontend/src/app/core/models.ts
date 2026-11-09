// Define the typed API records and reusable entity metadata used by CRUD screens.
export type ResourceKey =
  | 'usersins'
  | 'customers'
  | 'product-types'
  | 'policies'
  | 'claims';

export type ApiRecord = Record<string, unknown>;

export interface AuthUser {
  username: string;
  full_name: string;
  email: string;
  role: string;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface ProductTypeRecord {
  product_type: string;
  product_name: string;
}

export interface CustomerLookup {
  tckn_vkn: string;
  first_name: string;
  last_name: string;
  email: string | null;
  birth_date: string | null;
}

export interface PolicyRecord extends ApiRecord {
  policy_id: number;
  policy_no: string | null;
  tckn_vkn: string;
  product_type: string;
  start_date: string;
  end_date: string;
  premium_amount: string;
  status: string | null;
}

export interface ClaimPolicyContext extends PolicyRecord {
  first_name: string;
  last_name: string;
  email: string | null;
  birth_date: string | null;
}

export interface EntityField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'date' | 'number' | 'select' | 'textarea' | 'checkbox';
  required?: boolean;
  maxLength?: number;
  min?: number;
  options?: ReadonlyArray<{ value: string; label: string }>;
  immutableOnEdit?: boolean;
  blankLabel?: string;
}

export interface EntitySearchField {
  name: string;
  label: string;
  type?: 'text' | 'date' | 'select';
  blankLabel?: string;
  options?: ReadonlyArray<{ value: string; label: string }>;
}

export interface EntityDefinition {
  key: ResourceKey;
  title: string;
  singular: string;
  description: string;
  primaryKey: string;
  fields: ReadonlyArray<EntityField>;
  searchFields: ReadonlyArray<EntitySearchField>;
  columns: ReadonlyArray<{ name: string; label: string; format?: 'date' | 'money' | 'boolean' }>;
}
