const mongoose = require('mongoose');

const PuntoSchema = new mongoose.Schema({
  tipo: {
    type: String,
    enum: ['robo', 'secuestro', 'camara'],
    required: true
  },
  lat: {
    type: Number,
    required: true
  },
  lng: {
    type: Number,
    required: true
  },
  titulo: {
    type: String,
    required: true,
    trim: true
  },
  descripcion: {
    type: String,
    required: true,
    trim: true
  },
  fecha: {
    type: String,
    default: new Date().toISOString().split('T')[0]
  },
  usuarioId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  direccion: {
    type: String,
    trim: true
  }
}, {
  timestamps: true
});

module.exports = mongoose.model('Punto', PuntoSchema);
