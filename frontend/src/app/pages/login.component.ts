// Provide the Turkish sign-in and public account-registration screen.
import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { AuthService, errorMessage } from '../core/auth.service';
import {
  passwordValidators,
  registrationEmailValidators,
  registrationNameValidators,
  usernameValidators
} from '../core/validators';

@Component({
  selector: 'kinsure-login',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  readonly mode = signal<'login' | 'register'>('login');
  readonly showPassword = signal(false);
  readonly busy = signal(false);
  readonly error = signal('');

  readonly form = new FormGroup({
    username: new FormControl('', { nonNullable: true, validators: usernameValidators() }),
    password: new FormControl('', { nonNullable: true, validators: passwordValidators() }),
    full_name: new FormControl('', { nonNullable: true }),
    email: new FormControl('', { nonNullable: true })
  });

  setMode(mode: 'login' | 'register'): void {
    this.mode.set(mode);
    this.error.set('');
    this.form.controls.password.reset('');
    if (mode === 'register') {
      this.form.controls.full_name.setValidators(registrationNameValidators());
      this.form.controls.email.setValidators(registrationEmailValidators());
    } else {
      this.form.controls.full_name.clearValidators();
      this.form.controls.email.clearValidators();
    }
    this.form.controls.full_name.updateValueAndValidity();
    this.form.controls.email.updateValueAndValidity();
  }

  togglePassword(): void {
    this.showPassword.update((visible) => !visible);
  }

  submit(): void {
    this.error.set('');
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.busy.set(true);
    const { username, password, full_name, email } = this.form.getRawValue();
    const login = (): void => {
      this.auth.login(username, password).subscribe({
        next: () => void this.router.navigate(['/app']),
        error: (error: unknown) => {
          this.error.set(errorMessage(error));
          this.busy.set(false);
        }
      });
    };

    if (this.mode() === 'register') {
      this.auth.register({ username, password, full_name, email }).subscribe({
        next: () => login(),
        error: (error: unknown) => {
          this.error.set(errorMessage(error));
          this.busy.set(false);
        }
      });
      return;
    }
    login();
  }
}
