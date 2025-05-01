// server/routes/ingest.js
const express = require("express");
const router = express.Router();
const Event = require("../models/Event"); // Adjust path as needed

router.post("/ingest", async (req, res) => {
  try {
    const events = req.body;
    const inserted = await Event.insertMany(events, { ordered: false });
    res.json({ inserted: inserted.length });
  } catch (err) {
    console.error(err);
    res.status(500).send("Error inserting events");
  }
});

module.exports = router;
