// File: client/src/pages/eventspage.js
import React, { useEffect, useState } from 'react';
import EventCard from '../components/eventcard';
import Filters from '../components/filters';
import Pagination from '../components/pagination';
import '../styles/eventspage.css';

function EventsPage() {
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [selectedVenues, setSelectedVenues] = useState([]);
  const [selectedDate, setSelectedDate] = useState('');
  const [page, setPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    fetch('https://tinyamp.onrender.com/api/events')
      .then(res => res.json())
      .then(data => {
        setEvents(data);
        setFilteredEvents(data);
      });
  }, []);

  useEffect(() => {
    let filtered = [...events];
    if (selectedVenues.length > 0) {
      filtered = filtered.filter(event => selectedVenues.includes(event.venue));
    }
    if (selectedDate) {
      filtered = filtered.filter(event => event.date === selectedDate);
    }
    setFilteredEvents(filtered);
    setPage(1);
  }, [selectedVenues, selectedDate, events]);

  const start = (page - 1) * itemsPerPage;
  const paginatedEvents = filteredEvents.slice(start, start + itemsPerPage);
  const totalPages = Math.ceil(filteredEvents.length / itemsPerPage);

  return (
    <div className="events-page">
      <aside className="filters-panel">
        <Filters
          events={events}
          selectedVenues={selectedVenues}
          setSelectedVenues={setSelectedVenues}
          selectedDate={selectedDate}
          setSelectedDate={setSelectedDate}
        />
      </aside>
      <main className="event-list">
        <h1>🎶 tinyamp.live</h1>
        {paginatedEvents.map(event => (
          <EventCard key={event._id} {...event} />
        ))}
        <Pagination page={page} setPage={setPage} totalPages={totalPages} />
      </main>
    </div>
  );
}

export default EventsPage;
