import React, { useState } from 'react';
import './App.css';
import config from './config';

function App() {
  const [isRegistering, setIsRegistering] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: ''
  });

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${config.API_URL}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        })
      });
      
      const data = await response.json();
      if (response.ok) {
        localStorage.setItem('token', data.token);
        window.location.reload(); // Refresh to load the main app
      } else {
        setError(data.error || 'Login failed');
      }
    } catch (err) {
      setError('Network error occurred');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${config.API_URL}/api/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      if (response.ok) {
        setIsRegistering(false);
        setError('Registration successful! Please login.');
        setFormData({ email: '', password: '', name: '' });
      } else {
        setError(data.error || 'Registration failed');
      }
    } catch (err) {
      setError('Network error occurred');
    }
  };

  return (
    <div className="App">
      <div className="auth-container">
        <h1>Streakie</h1>
        <p className="subtitle">Your Daily Productivity Tracker</p>
        
        {error && <div className="error">{error}</div>}
        
        {!isRegistering ? (
          <form onSubmit={handleLogin} className="auth-form">
            <h2>Login</h2>
            <input
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleInputChange}
              required
            />
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={formData.password}
              onChange={handleInputChange}
              required
            />
            <button type="submit">Login</button>
            <button 
              type="button" 
              onClick={() => setIsRegistering(true)}
              className="switch-auth"
            >
              Need an account? Register
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="auth-form">
            <h2>Register</h2>
            <input
              type="text"
              name="name"
              placeholder="Name"
              value={formData.name}
              onChange={handleInputChange}
              required
            />
            <input
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleInputChange}
              required
            />
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={formData.password}
              onChange={handleInputChange}
              required
            />
            <button type="submit">Register</button>
            <button 
              type="button" 
              onClick={() => setIsRegistering(false)}
              className="switch-auth"
            >
              Have an account? Login
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

export default App;
