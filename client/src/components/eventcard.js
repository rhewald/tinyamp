import React from 'react';
import './EventCard.css';

function EventCard({ artist, venue, date, time, link }) {
  return (
    <div className="event-card">
      <h2>{artist}</h2>
      <p><strong>{venue}</strong></p>
      <p>{date} at {time}</p>
      {link && (
        <a href={link} target="_blank" rel="noopener noreferrer" className="event-link">
          More info
        </a>
      )}
    </div>
  );
}

export default EventCard;

// client/src/components/Filters.js
import React from 'react';
import './Filters.css';

function Filters({ venues, selectedVenues, onVenueChange, onDateChange }) {
  return (
    <div className="filters">
      <div>
        <label>Filter by Venue:</label>
        {venues.map((venue) => (
          <label key={venue}>
            <input
              type="checkbox"
              value={venue}
              checked={selectedVenues.includes(venue)}
              onChange={() => onVenueChange(venue)}
            />
            {venue}
          </label>
        ))}
      </div>
      <div>
        <label>Filter by Date:</label>
        <input type="date" onChange={(e) => onDateChange(e.target.value)} />
      </div>
    </div>
  );
}

export default Filters;