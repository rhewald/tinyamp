import React, { useEffect, useState } from 'react';
import EventCard from '../components/EventCard';
import Filters from '../components/Filters';
import Pagination from '../components/Pagination';
import './eventspage.css';

function EventsPage() {
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [selectedVenues, setSelectedVenues] = useState([]);
  const [selectedDate, setSelectedDate] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const eventsPerPage = 6;

  useEffect(() => {
    fetch('https://tinyamp.onrender.com/api/events')
      .then(res => res.json())
      .then(data => {
        const sorted = [...data].sort((a, b) => new Date(a.sortDate || a.date) - new Date(b.sortDate || b.date));
        setEvents(sorted);
        setFilteredEvents(sorted);
      });
  }, []);

  const handleFilterChange = (venues, date) => {
    setSelectedVenues(venues);
    setSelectedDate(date);
    const filtered = events.filter(event => {
      const venueMatch = venues.length === 0 || venues.includes(event.venue);
      const dateMatch = !date || (event.sortDate === date);
      return venueMatch && dateMatch;
    });
    setFilteredEvents(filtered);
    setCurrentPage(1);
  };

  const indexOfLastEvent = currentPage * eventsPerPage;
  const indexOfFirstEvent = indexOfLastEvent - eventsPerPage;
  const currentEvents = filteredEvents.slice(indexOfFirstEvent, indexOfLastEvent);

  return (
    <div className="events-page">
      <h1 className="header">🎶 tinyamp.live</h1>
      <Filters events={events} onFilterChange={handleFilterChange} />
      <div className="event-list">
        {currentEvents.map(event => (
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
      <Pagination
        totalEvents={filteredEvents.length}
        eventsPerPage={eventsPerPage}
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
      />
    </div>
  );
}

export default EventsPage;
