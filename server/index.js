const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
const app = express();
require('dotenv').config();

app.use(cors());
app.use(express.json());

mongoose.connect(process.env.MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

const eventRoutes = require('./routes/events');
app.use('/api/events', eventRoutes);

app.listen(5000, () => {
  console.log('Server is running on port 5000');
});