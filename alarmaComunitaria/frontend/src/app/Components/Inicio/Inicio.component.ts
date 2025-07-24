import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { RouterModule } from '@angular/router';
import { StorageService } from '../../services/storage.service';
import { MapaComponent } from '../mapa/mapa.component';
import { AlertasComponent } from '../alertas/alertas.component';
import { NotificationButtonComponent } from '../notification-button/notification-button.component';
import { AlertPopupComponent } from '../alert-popup/alert-popup.component';
import { NotificationsPanelComponent } from '../notifications-panel/notifications-panel.component';
import { NotificationService } from '../../services/notification.service';
import { AuthService } from '../../auth/services/auth.service';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MapaComponent,
    AlertasComponent,
    NotificationButtonComponent,
    AlertPopupComponent,
    NotificationsPanelComponent
  ],
  templateUrl: "./Inicio.component.html",
  styleUrls: ["./Inicio.component.scss"]
})
export class DashboardComponent implements OnInit {
  userInfo: any = null;
  isConnected = false;
  isPanicPulsing = false;
  private panicPulseTimeout: any = null;
  showCameraStream = false;
  cameraStreamUrl = 'http://127.0.0.1:5001/'; // Ajusta si tu stream está en otro puerto o ruta

  constructor(
    private storageService: StorageService,
    private notificationService: NotificationService,
    private authService: AuthService,
    private http: HttpClient,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit() {
    const userStr = this.storageService.getItem('user');
    if (userStr) {
      this.userInfo = JSON.parse(userStr);
    }

    // Inicializar sistema de notificaciones solo en el navegador
    if (isPlatformBrowser(this.platformId)) {
      // El WebSocket ya se conectó en el login
      // Solo suscribirse al estado de conexión
      this.notificationService.isConnected$.subscribe(
        connected => this.isConnected = connected
      );
      // Suscribirse a notificaciones en tiempo real
      this.notificationService.newNotification$.subscribe(notification => {
        if (notification) {
          // Si la notificación viene de la cámara, mostrar el stream
          if (notification.sender && notification.sender.userId === 'camara-auto') {
            this.showCameraStream = true;
            this.disableRecording(); // Deshabilitar grabación
            // Opcional: Ocultar el stream después de cierto tiempo
            setTimeout(() => {
              this.showCameraStream = false;
              this.enableRecording(); // Habilitar grabación
            }, 20000); // 20 segundos
          }
        }
      });
    }
  }

  // Método para deshabilitar la grabación de video
  disableRecording() {
    const url = `${this.cameraStreamUrl}disable_recording`;
    this.http.get(url).subscribe({
      next: (response) => {
        console.log('📹 Grabación deshabilitada');
      },
      error: (error) => {
        console.error('Error al deshabilitar grabación:', error);
      }
    });
  }

  // Método para habilitar la grabación de video
  enableRecording() {
    const url = `${this.cameraStreamUrl}enable_recording`;
    this.http.get(url).subscribe({
      next: (response) => {
        console.log('📹 Grabación habilitada');
      },
      error: (error) => {
        console.error('Error al habilitar grabación:', error);
      }
    });
  }

  logout() {
    this.storageService.removeItem('auth_token');
    this.storageService.removeItem('user');
    window.location.href = '/login';
  }

  onPanicClick() {
    this.isPanicPulsing = true;
    // Llama al backend de sonido para activar la alarma
    this.http.post('http://localhost:5020/activar_alarma', {})
      .subscribe({
        next: (res) => {
          // No mostrar ningún mensaje si la alarma se activa correctamente
        },
        error: (err) => {
          alert('Error: alarma no conectada');
        }
      });
    if (this.panicPulseTimeout) {
      clearTimeout(this.panicPulseTimeout);
    }
    this.panicPulseTimeout = setTimeout(() => {
      this.isPanicPulsing = false;
    }, 10000); // 10 segundos
  }
}
