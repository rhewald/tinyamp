import React, { useEffect, useState } from 'react';
import EventCard from '../components/eventcard';

function EventsPage() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/api/events')
      .then(res => res.json())
      .then(data => setEvents(data));
  }, []);

  return (
    <div>
      <h1>🎶 tinyamp.live</h1>
      {events.map(event => (
        <EventCard
          key={event._id}
          artist={event.artist}
          venue={event.venue}
          date={event.date}
          time={event.time}
          link={event.link}
        />
      ))}
    </div>
  );
}

export default EventsPage;
