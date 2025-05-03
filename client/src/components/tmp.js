import React from 'react';
import './filters.css';

function Filters({ venues, selectedVenues, onVenueChange, dateRange, onDateChange }) {
  return (
    <div className="filters">
      <div>
        <label>Venue:</label>
        <select multiple value={selectedVenues} onChange={onVenueChange}>
          {venues.map(v => (
            <option key={v} value={v}>{v}</option>
          ))}
        </select>
      </div>
      <div>
        <label>Date range:</label>
        <input type="date" value={dateRange.from} onChange={e => onDateChange('from', e.target.value)} />
        <input type="date" value={dateRange.to} onChange={e => onDateChange('to', e.target.value)} />
      </div>
    </div>
  );
}

export default filters;
