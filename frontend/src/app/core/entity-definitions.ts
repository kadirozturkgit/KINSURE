// Describe each backend CRUD resource, search fields, columns, and form validation metadata.
import { EntityDefinition, ResourceKey } from './models';

const genderOptions = [
  { value: 'E', label: 'Erkek' },
  { value: 'K', label: 'Kadın' },
  { value: 'X', label: 'Belirtmek istemiyor' }
] as const;

const statusOptions = [
  { value: 'ACTIVE', label: 'Aktif' },
  { value: 'CANCELLED', label: 'İptal edildi' },
  { value: 'EXPIRED', label: 'Süresi doldu' }
] as const;

const claimStatusOptions = [
  { value: 'OPEN', label: 'Açık' },
  { value: 'REVIEW', label: 'İncelemede' },
  { value: 'APPROVED', label: 'Onaylandı' },
  { value: 'REJECTED', label: 'Reddedildi' },
  { value: 'PAID', label: 'Ödendi' }
] as const;

const definitions: Record<ResourceKey, EntityDefinition> = {
  usersins: {
    key: 'usersins',
    title: 'Kullanıcılar',
    singular: 'kullanıcı',
    description: 'Sisteme erişen kullanıcıları ve hesap durumlarını yönetin.',
    primaryKey: 'username',
    searchFields: [
      { name: 'username', label: 'Kullanıcı adı' },
      { name: 'full_name', label: 'Ad soyad' }
    ],
    fields: [
      { name: 'username', label: 'Kullanıcı adı', type: 'text', required: true, maxLength: 20, immutableOnEdit: true },
      { name: 'password', label: 'Şifre', type: 'password', required: true, maxLength: 128 },
      { name: 'full_name', label: 'Ad soyad', type: 'text', required: true, maxLength: 100 },
      { name: 'email', label: 'E-posta', type: 'email', required: true, maxLength: 100 },
      { name: 'role', label: 'Rol', type: 'select', required: true, options: [
        { value: 'USER', label: 'Kullanıcı' },
        { value: 'ADMIN', label: 'Yönetici' }
      ] },
      { name: 'is_active', label: 'Hesap etkin', type: 'checkbox' }
    ],
    columns: [
      { name: 'username', label: 'Kullanıcı adı' },
      { name: 'full_name', label: 'Ad soyad' },
      { name: 'email', label: 'E-posta' },
      { name: 'role', label: 'Rol' },
      { name: 'is_active', label: 'Durum', format: 'boolean' }
    ]
  },
  customers: {
    key: 'customers',
    title: 'Müşteriler',
    singular: 'müşteri',
    description: 'Müşteri iletişim ve kimlik bilgilerini yönetin.',
    primaryKey: 'tckn_vkn',
    searchFields: [
      { name: 'tckn_vkn', label: 'TCKN / VKN' },
      { name: 'name', label: 'Ad veya soyad' }
    ],
    fields: [
      { name: 'tckn_vkn', label: 'TCKN / VKN', type: 'text', required: true, maxLength: 11, immutableOnEdit: true },
      { name: 'first_name', label: 'Ad', type: 'text', required: true, maxLength: 50 },
      { name: 'last_name', label: 'Soyad', type: 'text', required: true, maxLength: 50 },
      { name: 'email', label: 'E-posta', type: 'email', maxLength: 100 },
      { name: 'phone', label: 'Telefon', type: 'text', required: true, maxLength: 20 },
      { name: 'birth_date', label: 'Doğum tarihi', type: 'date' },
      { name: 'gender', label: 'Cinsiyet', type: 'select', blankLabel: 'Seçiniz', options: genderOptions },
      { name: 'address', label: 'Adres', type: 'textarea', maxLength: 500 }
    ],
    columns: [
      { name: 'tckn_vkn', label: 'TCKN / VKN' },
      { name: 'first_name', label: 'Ad' },
      { name: 'last_name', label: 'Soyad' },
      { name: 'phone', label: 'Telefon' },
      { name: 'email', label: 'E-posta' },
      { name: 'birth_date', label: 'Doğum tarihi', format: 'date' }
    ]
  },
  'product-types': {
    key: 'product-types',
    title: 'Ürün türleri',
    singular: 'ürün türü',
    description: 'Poliçelerde kullanılabilecek sigorta ürünlerini tanımlayın.',
    primaryKey: 'product_type',
    searchFields: [{ name: 'name', label: 'Ürün adı' }],
    fields: [
      { name: 'product_type', label: 'Ürün kodu', type: 'text', required: true, maxLength: 5, immutableOnEdit: true },
      { name: 'product_name', label: 'Ürün adı', type: 'text', required: true, maxLength: 50 }
    ],
    columns: [
      { name: 'product_type', label: 'Ürün kodu' },
      { name: 'product_name', label: 'Ürün adı' }
    ]
  },
  policies: {
    key: 'policies',
    title: 'Poliçeler',
    singular: 'poliçe',
    description: 'Müşterilere ait poliçeleri ve teminat sürelerini yönetin.',
    primaryKey: 'policy_id',
    searchFields: [
      { name: 'tckn_vkn', label: 'TCKN / VKN' },
      { name: 'product_type', label: 'Ürün türü', type: 'select', blankLabel: 'Tüm ürünler' },
      { name: 'start_date', label: 'Başlangıç', type: 'date' },
      { name: 'end_date', label: 'Bitiş', type: 'date' },
      { name: 'status', label: 'Durum', type: 'select', blankLabel: 'Tüm durumlar', options: statusOptions }
    ],
    fields: [
      { name: 'tckn_vkn', label: 'TCKN / VKN', type: 'text', required: true, maxLength: 11 },
      { name: 'product_type', label: 'Ürün türü', type: 'select', required: true, blankLabel: 'Ürün türü seçin' },
      { name: 'start_date', label: 'Başlangıç tarihi', type: 'date', required: true },
      { name: 'end_date', label: 'Bitiş tarihi', type: 'date', required: true },
      { name: 'premium_amount', label: 'Prim tutarı (₺)', type: 'number', required: true, min: 0 },
      { name: 'status', label: 'Durum', type: 'select', required: true, options: statusOptions }
    ],
    columns: [
      { name: 'policy_id', label: 'Poliçe ID' },
      { name: 'policy_no', label: 'Poliçe numarası' },
      { name: 'tckn_vkn', label: 'TCKN / VKN' },
      { name: 'product_type', label: 'Ürün türü' },
      { name: 'start_date', label: 'Başlangıç', format: 'date' },
      { name: 'end_date', label: 'Bitiş', format: 'date' },
      { name: 'premium_amount', label: 'Prim', format: 'money' },
      { name: 'status', label: 'Durum' }
    ]
  },
  claims: {
    key: 'claims',
    title: 'Hasarlar',
    singular: 'hasar kaydı',
    description: 'Hasar bildirimlerini, ödeme tutarlarını ve durumlarını izleyin.',
    primaryKey: 'claim_id',
    searchFields: [
      { name: 'policy_id', label: 'Poliçe ID' },
      { name: 'claim_no', label: 'Hasar numarası' }
    ],
    fields: [
      { name: 'policy_id', label: 'Poliçe ID', type: 'number', required: true, min: 1 },
      { name: 'incident_date', label: 'Hasar tarihi', type: 'date', required: true },
      { name: 'claim_date', label: 'Bildirim tarihi', type: 'date', required: true },
      { name: 'claim_amount', label: 'Hasar tutarı (₺)', type: 'number', required: true, min: 0 },
      { name: 'paid_amount', label: 'Ödenen tutar (₺)', type: 'number', min: 0 },
      { name: 'status', label: 'Durum', type: 'select', required: true, options: claimStatusOptions },
      { name: 'description', label: 'Açıklama', type: 'textarea', maxLength: 1000 }
    ],
    columns: [
      { name: 'claim_no', label: 'Hasar numarası' },
      { name: 'policy_id', label: 'Poliçe ID' },
      { name: 'incident_date', label: 'Hasar tarihi', format: 'date' },
      { name: 'claim_date', label: 'Bildirim tarihi', format: 'date' },
      { name: 'claim_amount', label: 'Hasar tutarı', format: 'money' },
      { name: 'paid_amount', label: 'Ödenen', format: 'money' },
      { name: 'status', label: 'Durum' }
    ]
  }
};

export function entityDefinition(key: ResourceKey): EntityDefinition {
  return definitions[key];
}
