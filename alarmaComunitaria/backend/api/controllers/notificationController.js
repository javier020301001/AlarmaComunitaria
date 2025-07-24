// Controlador de notificaciones
let wsServer;

const setWebSocketServer = (server) => {
  wsServer = server;
};

const Notification = require('../models/Notification');

// Usuarios conectados y su ubicación
const connectedUsers = new Map(); // userId -> { lat, lon, ws }

// Haversine para distancia en km
function calcularDistancia(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const toRad = deg => deg * Math.PI / 180;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

// Recibir estado de la cámara
const recibirEstado = async (req, res) => {
  try {
    const { status } = req.body;
    if (!status) {
      return res.status(400).json({ error: "Falta el campo 'status'" });
    }
    // Guardar en Mongo
    await Notification.create({ status });
    // Notificar a todos los clientes conectados (sin filtro de cercanía)
    wsServer.broadcast({ type: 'evento', status });
    return res.json({ status: true, message: 'Solicitud recibida' });
  } catch (error) {
    console.error('Error en recibirEstado:', error);
    res.status(500).json({ message: 'Error interno del servidor' });
  }
};

// Recibir detalle de la cámara
const recibirDetalleCamara = async (req, res) => {
  try {
    const data = req.body;
    console.log('📷 Detalle recibido de camara.py:', JSON.stringify(data, null, 2)); // <-- Log detallado
    // Mostrar en consola toda la información recibida
    console.log('🔔 Información recibida desde BACK-ENDV2:', JSON.stringify(data, null, 2));
    if (!data || !data.nombre_camara || !data.ubicacion || !data.fecha || !data.alerta || !data.informacion_extra) {
      return res.status(400).json({ error: 'Faltan campos' });
    }
    // Guardar en Mongo
    await Notification.create({ detalle: data, ubicacion: data.ubicacion, alertType: data.alerta, extra: data.informacion_extra });
    // Crear notificación estándar para WebSocket
    const notification = {
      id: Date.now().toString(36) + Math.random().toString(36).substr(2),
      title: `Alerta automática: ${data.alerta}`,
      message: `Cámara ${data.nombre_camara} detectó: ${data.alerta} el ${data.fecha}`,
      timestamp: new Date(),
      isRead: false,
      sender: {
        userId: 'camara-auto',
        email: 'camara@alarma.com',
        name: data.nombre_camara || 'Cámara'
      },
      metadata: {
        alertType: data.alerta,
        location: typeof data.ubicacion === 'object' && data.ubicacion.lat && data.ubicacion.lon
          ? `${data.ubicacion.lat}, ${data.ubicacion.lon}`
          : (typeof data.ubicacion === 'string' ? data.ubicacion : ''),
        lat: data.ubicacion?.lat,
        lng: data.ubicacion?.lon,
        imageUrl: data.informacion_extra?.imageUrl || null
      }
    };
    // Agregar a la lista global de notificaciones
    wsServer.getNotifications().push(notification);
    // Mantener solo las últimas 100
    if (wsServer.getNotifications().length > 100) {
      wsServer.getNotifications().splice(0, wsServer.getNotifications().length - 100);
    }
    // Notificar a todos los clientes conectados
    wsServer.broadcast({ type: 'new_notification', notification });
    // Además, emitir el evento específico de cámara (opcional)
    wsServer.broadcast({ type: 'actualizar_camara', detalle: data }, data.ubicacion);
    return res.json({ mensaje: 'Detalle recibido correctamente' });
  } catch (error) {
    console.error('Error en recibirDetalleCamara:', error);
    res.status(500).json({ message: 'Error interno del servidor' });
  }
};

// WebSocket: registrar ubicación
const registrarUbicacion = (userId, lat, lon, ws) => {
  connectedUsers.set(userId, { lat, lon, ws });
};

// WebSocket: desconectar usuario
const desconectarUsuario = (userId) => {
  connectedUsers.delete(userId);
};

// WebSocket: notificar solo a usuarios cercanos
const notificarUsuariosCercanos = (ubicacion, payload) => {
  for (const [userId, info] of connectedUsers.entries()) {
    if (info.lat != null && info.lon != null) {
      const dist = calcularDistancia(info.lat, info.lon, ubicacion.lat, ubicacion.lon);
      if (dist <= 1) {
        info.ws.send(JSON.stringify(payload));
      }
    }
  }
};

// Enviar notificación (requiere autenticación)
const sendNotification = (req, res) => {
  try {
    const { title, message, alertType, location, imageUrl } = req.body;
    if (!title || !message || !location) {
      return res.status(400).json({
        message: 'Título, mensaje y ubicación son requeridos'
      });
    }
    const notification = {
      id: Date.now().toString(36) + Math.random().toString(36).substr(2),
      title,
      message,
      timestamp: new Date(),
      isRead: false,
      sender: {
        userId: req.user.userId,
        email: req.user.email,
        name: req.user.name
      },
      metadata: {
        alertType: alertType || 'general',
        location,
        imageUrl
      }
    };
    
    const notifications = wsServer.getNotifications();
    notifications.push(notification);
    wsServer.broadcast({ type: 'new_notification', notification });
    res.status(201).json(notification);
  } catch (error) {
    console.error('Error creando notificación:', error);
    res.status(500).json({ message: 'Error interno del servidor' });
  }
};

// Obtener notificaciones (requiere autenticación)
const getNotifications = (req, res) => {
  try {
    const notifications = wsServer.getNotifications();
    const sortedNotifications = notifications.sort((a, b) =>
      new Date(b.timestamp) - new Date(a.timestamp)
    );
    res.json(sortedNotifications);
  } catch (error) {
    console.error('Error obteniendo notificaciones:', error);
    res.status(500).json({ message: 'Error interno del servidor' });
  }
};

// Notificación de prueba
const testNotification = (req, res) => {
  try {
    const { title, message, alertType, location, imageUrl } = req.body;
    const notification = {
      id: Date.now().toString(36) + Math.random().toString(36).substr(2),
      title: title || 'Alerta de Prueba',
      message: message || 'Esta es una notificación de prueba',
      timestamp: new Date(),
      isRead: false,
      sender: {
        userId: 'test-user',
        email: 'test@example.com',
        name: 'Test User'
      },
      metadata: {
        alertType: alertType || 'general',
        location: location || 'Quito, Ecuador',
        imageUrl: imageUrl || 'https://via.placeholder.com/300x200'
      }
    };
    const notifications = wsServer.getNotifications();
    notifications.push(notification);
    wsServer.broadcast({ type: 'new_notification', notification });
    res.json({
      success: true,
      notification,
      connectedClients: wsServer.getConnectedClients().length
    });
  } catch (error) {
    console.error('Error creando notificación de prueba:', error);
    res.status(500).json({ message: 'Error interno del servidor' });
  }
};

// Ver clientes conectados
const getConnectedClients = (req, res) => {
  const clients = wsServer.getConnectedClients();
  res.json({
    connectedClients: clients,
    count: clients.length
  });
};

module.exports = {
  setWebSocketServer,
  sendNotification,
  getNotifications,
  testNotification,
  getConnectedClients,
  recibirEstado,
  recibirDetalleCamara,
  registrarUbicacion,
  desconectarUsuario,
  notificarUsuariosCercanos
};
