const mongoose = require('mongoose');

const NotificationSchema = new mongoose.Schema({
  status: {
    type: String,
    required: false
  },
  detalle: {
    type: Object,
    required: false
  },
  alertType: {
    type: String,
    default: 'general'
  },
  ubicacion: {
    lat: Number,
    lon: Number
  },
  cercano: {
    type: Boolean,
    default: false
  },
  timestamp: {
    type: Date,
    default: Date.now
  },
  extra: {
    type: Object,
    required: false
  }
}, {
  timestamps: true
});

module.exports = mongoose.model('Notification', NotificationSchema); 