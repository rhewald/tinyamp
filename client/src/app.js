import React, { useEffect, useState } from 'react';

function App() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/api/events')
      .then(res => res.json())
      .then(data => setEvents(data));
  }, []);

  return (
    <div className="App">
      <h1>🎶 tinyamp.live</h1>
      <ul>
        {events.map(e => (
          <li key={e._id}>{e.artist} @ {e.venue} on {e.date} at {e.time}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;