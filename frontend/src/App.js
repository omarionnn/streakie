import React, { useState, useEffect } from 'react';
import './App.css';
import config from './config';

function App() {
  const [status, setStatus] = useState('Loading...');

  useEffect(() => {
    // Test connection to backend
    fetch(`${config.API_URL}/health`)
      .then(response => response.text())
      .then(data => setStatus(data))
      .catch(error => setStatus('Error connecting to backend'));
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Streakie</h1>
        <p>Backend Status: {status}</p>
      </header>
    </div>
  );
}

export default App;
