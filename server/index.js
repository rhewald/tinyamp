const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
require('dotenv').config();

const app = express();

app.use(cors());
app.use(express.json());

// Health check route
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', message: 'TinyAmp server is live!' });
});

// MongoDB connection
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log('✅ MongoDB connected'))
  .catch((err) => console.error('❌ MongoDB connection error:', err));

// Routes
const eventRoutes = require('./routes/events');
const ingestRoutes = require('./routes/ingest');

app.use('/api/events', eventRoutes);
app.use('/api', ingestRoutes);

// Start server
const port = process.env.PORT || 3001;
app.listen(port, () => {
  console.log(`🚀 Server is running on port ${port}`);
});
