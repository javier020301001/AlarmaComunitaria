import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { Notification } from '../Share/interface/notification.interface';

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket: WebSocket | null = null;
  private connectionStatus = new BehaviorSubject<boolean>(false);
  private notificationSubject = new Subject<Notification>();
  private reconnectTimeout: any = null;

  public connectionStatus$ = this.connectionStatus.asObservable();
  public notifications$ = this.notificationSubject.asObservable();

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {}

  connect(token: string): void {
    // Solo conectar WebSocket en el navegador
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      // Conectar al WebSocket con el token JWT
      this.socket = new WebSocket(`ws://localhost:3000/ws?token=${token}`);

      this.socket.onopen = () => {
        this.connectionStatus.next(true);
        if (this.reconnectTimeout) {
          clearTimeout(this.reconnectTimeout);
          this.reconnectTimeout = null;
        }
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'new_notification') {
            this.notificationSubject.next(data.notification);
          } else if (data.type === 'notification_updated') {
            // Manejar actualización de notificación
          } else if (data.type === 'all_notifications_read') {
            // Manejar todas las notificaciones marcadas como leídas
          } else if (data.type === 'notification_deleted') {
            // Manejar eliminación de notificación
          } else if (data.type === 'notifications_list') {
            // Procesar lista de notificaciones existentes
            data.notifications.forEach((notification: any) => {
              this.notificationSubject.next(notification);
            });
          }
        } catch (error) {
        }
      };

      this.socket.onclose = (event) => {
        this.connectionStatus.next(false);
        // Reconectar automáticamente después de 5 segundos
        if (this.reconnectTimeout) {
          clearTimeout(this.reconnectTimeout);
        }
        this.reconnectTimeout = setTimeout(() => {
          if (token) {
            this.connect(token);
          }
        }, 5000);
      };

      this.socket.onerror = (error) => {
        this.connectionStatus.next(false);
        // Cerrar el socket para forzar reconexión
        if (this.socket && this.socket.readyState !== WebSocket.CLOSED) {
          this.socket.close();
        }
      };

    } catch (error) {
      this.connectionStatus.next(false);
    }
  }

  // Método público para reconectar manualmente
  reconnect(token: string): void {
    if (this.socket) {
      try {
        this.socket.close();
      } catch (e) {}
      this.socket = null;
    }
    this.connect(token);
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  sendNotification(notification: any): void {
    // Solo enviar en el navegador
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      const message = {
        type: 'send_notification',
        notification
      };
      this.socket.send(JSON.stringify(message));
    }
  }

  isConnected(): boolean {
    if (!isPlatformBrowser(this.platformId)) {
      return false;
    }
    return this.socket?.readyState === WebSocket.OPEN;
  }
}
