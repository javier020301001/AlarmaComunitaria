import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, FormGroup } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import { StorageService } from '../../services/storage.service';
import { NotificationService } from '../../services/notification.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  loginForm: FormGroup;
  errorMessage: string = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private storageService: StorageService,
    private notificationService: NotificationService
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  onSubmit() {
    if (this.loginForm.valid) {
      this.errorMessage = ''; // Limpiar mensajes de error previos

      // Mostrar estado de carga
      const submitButton = document.querySelector('.submit-button') as HTMLButtonElement;
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Iniciando sesión...';
      }

      this.authService.login(this.loginForm.value).subscribe({
        next: (response) => {
          // El token JWT ya se guarda en el AuthService
          // Conectar WebSocket después del login exitoso
          this.notificationService.connectWebSocket();

          // Navegar al dashboard
          this.router.navigate(['/dashboard']);
        },
        error: (err: any) => {
          this.errorMessage = 'Error al iniciar sesión. Verifica tus credenciales.';

          // Restaurar botón
          if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = 'Ingresar';
          }
        },
        complete: () => {
          // Restaurar botón en caso de éxito
          if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = 'Ingresar';
          }
        }
      });
    }
  }
}
