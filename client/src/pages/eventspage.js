import React, { useEffect, useState } from 'react';
import EventCard from '../components/eventcard';
import Filters from '../components/filters';
import Pagination from '../components/pagination';
import './eventspage.css';

function EventsPage() {
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [selectedVenue, setSelectedVenue] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const EVENTS_PER_PAGE = 10;

  useEffect(() => {
    fetch('https://tinyamp.onrender.com/api/events')
      .then(res => res.json())
      .then(data => {
        const sorted = data
          .filter(e => e.sortDate)
          .sort((a, b) => new Date(a.sortDate) - new Date(b.sortDate));
        setEvents(sorted);
        setFilteredEvents(sorted);
      });
  }, []);

  useEffect(() => {
    const filtered = events.filter(event => {
      const venueMatch = selectedVenue ? event.venue === selectedVenue : true;
      const dateMatch = selectedDate ? event.sortDate === selectedDate : true;
      return venueMatch && dateMatch;
    });
    setFilteredEvents(filtered);
    setCurrentPage(1);
  }, [selectedVenue, selectedDate, events]);

  const start = (currentPage - 1) * EVENTS_PER_PAGE;
  const currentEvents = filteredEvents.slice(start, start + EVENTS_PER_PAGE);
  const venues = [...new Set(events.map(event => event.venue))];

  return (
    <div className="events-page">
      <h1 className="headline">🎶 tinyamp.live</h1>
      <Filters
        venues={venues}
        selectedVenue={selectedVenue}
        setSelectedVenue={setSelectedVenue}
        selectedDate={selectedDate}
        setSelectedDate={setSelectedDate}
      />
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
      <Pagination
        currentPage={currentPage}
        totalPages={Math.ceil(filteredEvents.length / EVENTS_PER_PAGE)}
        onPageChange={setCurrentPage}
      />
    </div>
  );
}

export default EventsPage;
