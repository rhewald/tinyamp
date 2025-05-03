import React, { useEffect, useState } from 'react';
import EventCard from '../components/eventcard';
import Filters from '../components/filters';
import Pagination from '../components/pagination';
import './eventspage.css';

function EventsPage() {
  const [events, setEvents] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [venues, setVenues] = useState([]);
  const [selectedVenues, setSelectedVenues] = useState([]);
  const [selectedDate, setSelectedDate] = useState('');
  const [page, setPage] = useState(1);
  const perPage = 10;

  useEffect(() => {
    fetch('https://tinyamp.onrender.com/api/events')
      .then(res => res.json())
      .then(data => {
        const sorted = data.sort((a, b) => new Date(a.sortDate) - new Date(b.sortDate));
        setEvents(sorted);
        setFiltered(sorted);
        setVenues([...new Set(sorted.map(ev => ev.venue))]);
      });
  }, []);

  useEffect(() => {
    let filteredData = [...events];
    if (selectedVenues.length > 0) {
      filteredData = filteredData.filter(ev => selectedVenues.includes(ev.venue));
    }
    if (selectedDate) {
      filteredData = filteredData.filter(ev => ev.sortDate === selectedDate);
    }
    setFiltered(filteredData);
    setPage(1);
  }, [selectedVenues, selectedDate]);

  const paginatedEvents = filtered.slice((page - 1) * perPage, page * perPage);

  return (
    <div className="events-page">
      <h1>🎶 tinyamp.live</h1>
      <Filters
        venues={venues}
        selectedVenues={selectedVenues}
        setSelectedVenues={setSelectedVenues}
        selectedDate={selectedDate}
        setSelectedDate={setSelectedDate}
      />
      <div className="event-grid">
        {paginatedEvents.map(event => (
          <EventCard key={event._id} {...event} />
        ))}
      </div>
      <Pagination
        page={page}
        total={filtered.length}
        perPage={perPage}
        setPage={setPage}
      />
    </div>
  );
}

export default eventspage;
