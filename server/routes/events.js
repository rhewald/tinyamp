const express = require('express');
const router = express.Router();
const Event = require('../models/Event');

// GET /api/events?date=2025-05-01&venue=The%20Chapel
router.get('/', async (req, res) => {
  const filters = req.query;
  const query = {};
  if (filters.date) query.date = filters.date;
  if (filters.venue) query.venue = filters.venue;
  if (filters.artist) query.artist = { $regex: filters.artist, $options: 'i' };

  const events = await Event.find(query);
  res.json(events);
});

module.exports = router;