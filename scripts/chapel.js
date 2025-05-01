const puppeteer = require('puppeteer');
const mongoose = require('mongoose');
require('dotenv').config({ path: './server/.env' });
const Event = require('../server/models/Event');

(async () => {
  await mongoose.connect(process.env.MONGO_URI);
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('https://thechapelsf.com/', { waitUntil: 'networkidle2' });

  const events = await page.evaluate(() => {
    const rows = document.querySelectorAll('div.views-row');
    const data = [];

    rows.forEach(row => {
      const artist = row.querySelector('.field--name-title')?.innerText?.trim();
      const dateText = row.querySelector('.field--name-field-event-date')?.innerText?.trim();
      const image = row.querySelector('img')?.src || '';

      let date = '';
      let time = '';

      if (dateText?.includes('|')) {
        [date, time] = dateText.split('|').map(t => t.trim());
      } else {
        date = dateText;
      }

      if (artist && date) {
        data.push({
          artist,
          venue: 'The Chapel',
          date,
          time,
          image,
          socials: {}
        });
      }
    });

    return data;
  });

  await browser.close();

  console.log(`Scraped ${events.length} events...`);
  await Event.deleteMany({ venue: 'The Chapel' });
  await Event.insertMany(events);
  console.log(`Inserted ${events.length} events from The Chapel.`);
  process.exit();
})();
