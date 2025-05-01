const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
require('dotenv').config();

const app = express();

app.use(cors());
app.use(express.json());

// MongoDB connection
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log('MongoDB connected'))
  .catch((err) => console.error('MongoDB connection error:', err));

// Routes
const eventRoutes = require('./routes/events');
const ingestRoutes = require('./routes/ingest');

app.use('/api/events', eventRoutes);
app.use('/api', ingestRoutes);

// Start server *after* routes are registered
app.listen(5000, () => {
  console.log('Server is running on port 5000');
});
