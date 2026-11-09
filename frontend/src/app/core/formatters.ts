// Convert calendar values and API values to the DD/MM/YYYY contract.
export function toApiDate(value: string): string {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  return match ? `${match[3]}/${match[2]}/${match[1]}` : value;
}

export function toInputDate(value: unknown): string {
  if (typeof value !== 'string') {
    return '';
  }

  const localDate = /^(\d{2})\/(\d{2})\/(\d{4})/.exec(value);
  if (localDate) {
    return `${localDate[3]}-${localDate[2]}-${localDate[1]}`;
  }

  const isoDate = /^(\d{4})-(\d{2})-(\d{2})/.exec(value);
  return isoDate ? `${isoDate[1]}-${isoDate[2]}-${isoDate[3]}` : '';
}

export function formatDate(value: unknown): string {
  if (typeof value !== 'string' || value.length === 0) {
    return '—';
  }
  const inputDate = toInputDate(value);
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(inputDate);
  return match ? `${match[3]}/${match[2]}/${match[1]}` : value;
}

export function formatMoney(value: unknown): string {
  const amount = Number(value);
  return Number.isFinite(amount)
    ? new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(amount)
    : '—';
}
