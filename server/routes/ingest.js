const express = require('express');
const router = express.Router();
const Event = require('../models/Event'); // Adjust path if needed

router.post('/ingest', async (req, res) => {
  try {
    const events = req.body;

    if (!Array.isArray(events)) {
      return res.status(400).json({ message: 'Expected an array of events' });
    }

    // Optional: clear existing events before inserting (only if you want to avoid duplicates)
    // await Event.deleteMany({ venue: "The Chapel" });

    const inserted = await Event.insertMany(events);
    res.status(200).json({ message: `Inserted ${inserted.length} events.` });
  } catch (error) {
    console.error("Ingest error:", error);
    res.status(500).json({ message: 'Server error while ingesting events' });
  }
});

module.exports = router;
