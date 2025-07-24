export interface Notification {
  id: string;
  title: string;
  message: string;
  timestamp: Date;
  isRead: boolean;
  metadata?: {
    alertType: string;
    location: string;
    lat?: number;
    lng?: number;
    imageUrl?: string;
  };
  sender?: {
    userId: string;
    email?: string;
    name?: string;
  };
}

export interface NotificationPayload {
  title: string;
  message: string;
  alertType: string;
  location: string;
  lat?: number;
  lng?: number;
  imageUrl?: string;
}
