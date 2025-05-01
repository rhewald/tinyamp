const express = require('express');
const router = express.Router();
const Event = require('../models/Event');

// GET /api/events?date=2025-05-01&venue=The%20Chapel&artist=ArtistName
router.get('/', async (req, res) => {
  const filters = req.query;
  const query = {};
  if (filters.date) query.date = filters.date;
  if (filters.venue) query.venue = filters.venue;
  if (filters.artist) query.artist = { $regex: filters.artist, $options: 'i' };

  try {
    const events = await Event.find(query);
    res.json(events);
  } catch (err) {
    res.status(500).json({ message: "Error fetching events", error: err });
  }
});

// GET /api/events/test - Fetch 10 most recent events from The Chapel
router.get('/test', async (req, res) => {
  try {
    const events = await Event.find({ venue: "The Chapel" })
      .sort({ _id: -1 })
      .limit(10);
    res.json(events);
  } catch (err) {
    console.error("Test fetch error:", err);
    res.status(500).json({ message: "Could not fetch events", error: err });
  }
});

// POST /api/events - Bulk insert of events
router.post('/', async (req, res) => {
  try {
    const events = req.body;
    if (!Array.isArray(events)) {
      return res.status(400).json({ message: 'Expected an array of events' });
    }

    const saved = await Event.insertMany(events, { ordered: false });
    res.status(200).json({ message: 'Events saved', count: saved.length });
  } catch (err) {
    console.error('Insert error:', err);
    res.status(500).json({ message: 'Failed to save events', error: err.message });
  }
});

module.exports = router;
