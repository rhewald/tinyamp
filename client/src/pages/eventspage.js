import React, { useEffect, useState } from 'react';
import EventCard from '../components/eventcard';
import './eventspage.css';

function EventsPage() {
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [venues, setVenues] = useState([]);
  const [selectedVenues, setSelectedVenues] = useState([]);
  const [selectedDate, setSelectedDate] = useState('');
  const [page, setPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    fetch('https://tinyamp.onrender.com/api/events')
      .then(res => res.json())
      .then(data => {
        const sorted = [...data].sort((a, b) => new Date(a.sortDate) - new Date(b.sortDate));
        setEvents(sorted);
        setFilteredEvents(sorted);
        const uniqueVenues = [...new Set(data.map(e => e.venue))];
        setVenues(uniqueVenues);
      });
  }, []);

  useEffect(() => {
    let updated = [...events];
    if (selectedVenues.length > 0) {
      updated = updated.filter(e => selectedVenues.includes(e.venue));
    }
    if (selectedDate) {
      updated = updated.filter(e => e.sortDate === selectedDate);
    }
    setFilteredEvents(updated);
    setPage(1);
  }, [selectedVenues, selectedDate, events]);

  const handleVenueToggle = (venue) => {
    setSelectedVenues(prev =>
      prev.includes(venue) ? prev.filter(v => v !== venue) : [...prev, venue]
    );
  };

  const handleDateChange = (e) => {
    setSelectedDate(e.target.value);
  };

  const totalPages = Math.ceil(filteredEvents.length / itemsPerPage);
  const paginated = filteredEvents.slice((page - 1) * itemsPerPage, page * itemsPerPage);

  return (
    <div>
      <h1>🎶 tinyamp.live</h1>

      <div className="filters">
        <div>
          <label>Select Date:</label>
          <input type="date" value={selectedDate} onChange={handleDateChange} />
        </div>
        <div>
          <label>Filter by Venue:</label>
          {venues.map(v => (
            <label key={v}>
              <input
                type="checkbox"
                checked={selectedVenues.includes(v)}
                onChange={() => handleVenueToggle(v)}
              />
              {v}
            </label>
          ))}
        </div>
      </div>

      {paginated.map(event => (
        <EventCard
          key={event._id}
          artist={event.artist}
          venue={event.venue}
          date={event.date}
          time={event.time}
          link={event.link}
        />
      ))}

      <div className="pagination">
        {Array.from({ length: totalPages }, (_, i) => (
          <button key={i + 1} onClick={() => setPage(i + 1)} disabled={page === i + 1}>
            {i + 1}
          </button>
        ))}
      </div>
    </div>
  );
}

export default EventsPage;
