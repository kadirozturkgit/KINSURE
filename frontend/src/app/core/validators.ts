// Keep Angular form rules in one place so all entity screens validate consistently.
import { AbstractControl, ValidationErrors, ValidatorFn, Validators } from '@angular/forms';

import { EntityDefinition, EntityField } from './models';

export function validatorsForField(field: EntityField): ValidatorFn[] {
  const validators: ValidatorFn[] = [];

  if (field.required) {
    validators.push(Validators.required);
  }
  if (field.maxLength !== undefined) {
    validators.push(Validators.maxLength(field.maxLength));
  }
  if (field.type === 'email') {
    validators.push(Validators.email);
  }
  if (field.type === 'number') {
    validators.push(Validators.min(field.min ?? 0));
    validators.push(numberValidator());
  }
  if (field.name === 'tckn_vkn') {
    validators.push(Validators.pattern(/^[0-9]{11}$/));
  }
  if (field.name === 'username') {
    validators.push(Validators.pattern(/^[A-Za-z0-9._-]+$/));
  }
  if (field.name === 'password') {
    validators.push(Validators.minLength(8));
  }
  if (field.name === 'gender') {
    validators.push(Validators.pattern(/^[EKX]$/));
  }

  return validators;
}

export function usernameValidators(): ValidatorFn[] {
  return [Validators.required, Validators.maxLength(20)];
}

export function passwordValidators(): ValidatorFn[] {
  return [Validators.required, Validators.minLength(8), Validators.maxLength(128)];
}

export function registrationNameValidators(): ValidatorFn[] {
  return [Validators.required, Validators.maxLength(100)];
}

export function registrationEmailValidators(): ValidatorFn[] {
  return [Validators.required, Validators.email, Validators.maxLength(100)];
}

export function crossFieldValidator(definition: EntityDefinition): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    if (definition.key === 'policies') {
      const start = control.get('start_date')?.value as string | undefined;
      const end = control.get('end_date')?.value as string | undefined;
      if (start && end && end <= start) {
        return { dateRange: true };
      }
    }
    if (definition.key === 'claims') {
      const claimAmount = Number(control.get('claim_amount')?.value ?? 0);
      const paidAmount = Number(control.get('paid_amount')?.value ?? 0);
      if (paidAmount > claimAmount) {
        return { paidAmount: true };
      }
    }
    return null;
  };
}

function numberValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    if (control.value === '' || control.value === null || control.value === undefined) {
      return null;
    }
    return Number.isFinite(Number(control.value)) ? null : { number: true };
  };
}
