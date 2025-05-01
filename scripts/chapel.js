const axios = require('axios');
const cheerio = require('cheerio');
const mongoose = require('mongoose');
require('dotenv').config({ path: './server/.env' });
const Event = require('../server/models/Event');

(async () => {
  await mongoose.connect(process.env.MONGO_URI);
  const url = 'https://thechapelsf.com/';
  const res = await axios.get(url);
  const $ = cheerio.load(res.data);

  const events = [];

  $('.event-list .event-item').each((i, el) => {
    const artist = $(el).find('.event-title').text().trim();
    const dateTime = $(el).find('.event-date').text().trim();
    const [date, time] = dateTime.split(' at ');
    const image = $(el).find('img').attr('src');

    if (artist && date) {
      events.push({
        artist,
        venue: 'The Chapel',
        date,
        time: time || '',
        image: image || '',
        socials: {}
      });
    }
  });

  await Event.deleteMany({ venue: 'The Chapel' });
  await Event.insertMany(events);
  console.log(`Inserted ${events.length} events from The Chapel.`);
  process.exit();
})();