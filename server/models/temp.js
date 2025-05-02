const mongoose = require('mongoose');
const EventSchema = new mongoose.Schema({
  artist: String,
  venue: String,
  date: String,
  time: String,
  image: String,
  socials: {
    instagram: String,
    spotify: String,
    youtube: String,
    website: String,
  },
});

module.exports = mongoose.model('Event', EventSchema);