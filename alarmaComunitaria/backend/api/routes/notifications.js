const express = require('express');
const notificationController = require('../controllers/notificationController');

module.exports = (wsServer, authenticateToken) => {
  notificationController.setWebSocketServer(wsServer);
  const router = express.Router();
  router.post('/', authenticateToken, notificationController.sendNotification);
  router.get('/', authenticateToken, notificationController.getNotifications);
  router.post('/test', notificationController.testNotification);
  router.get('/connected-clients', notificationController.getConnectedClients);
  // Agregado para recibir notificaciones desde BACK-ENDV2
  router.post('/detalle', notificationController.recibirDetalleCamara);
  router.post('/estado', notificationController.recibirEstado);
  return router;
};
