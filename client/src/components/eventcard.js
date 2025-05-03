import React from 'react';
import './eventcard.css';

function EventCard({ artist, venue, date, time, link }) {
  return (
    <div className="event-card">
      <h2>{artist}</h2>
      <p><strong>{venue}</strong></p>
      <p>{date} at {time}</p>
      {link && (
        <a
          href={link}
          target="_blank"
          rel="noopener noreferrer"
          className="event-link"
        >
          More info
        </a>
      )}
    </div>
  );
}

export default EventCard;
