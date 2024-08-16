// src/WelcomePage.js
import React, { useState } from 'react';
import './static/css/WelcomePage.css';
import logo from './static/images/spotify-logo.jpg'; //import the spotify logo image

const WelcomePage = () => {
  const [clientId, setClientId] = useState('');
  const [clientSecret, setClientSecret] = useState('');
  const [redirectUri, setRedirectUri] = useState('');
  const [openAiKey, setOpenAiKey] = useState('');
  const [youtubeKey, setYoutubeKey] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!clientId || !clientSecret || !redirectUri || !openAiKey || !youtubeKey) {
      setError('All fields are required.');
      return;
    }

    // Clear previous error message
    setError('');

    try {
      // Send data to the server
      const response = await fetch('http://localhost:5000/set-credentials', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          clientId,
          clientSecret,
          redirectUri,
          openAiKey,
          youtubeKey
        }),
        credentials: 'include'
      });

      if (!response.ok) throw new Error('Network response was not ok');

      // Redirect to login
      window.location.href = 'http://localhost:5000/login';
    } catch (error) {
      console.error('Fetch error:', error);
      setError('Failed to set credentials.');
    }
  };

  return (
    <div className="welcome-page">
      <div className="logo-container">
        <img src={logo} alt="Spotify Logo" className="logo" />
      </div>
      <div className="form-container">
        <h1>Welcome to My Spotify App</h1>
        <p>Please enter information to use the App</p>
        <form onSubmit={handleSubmit} className="login-form">
          <input type="text" placeholder="Spotify Client ID" value={clientId} onChange={(e) => setClientId(e.target.value)} required/>
          <input type="text" placeholder="Spotify Client Secret" value={clientSecret} onChange={(e) => setClientSecret(e.target.value)} required/>
          <input type="text" placeholder="Redirect URI" value={redirectUri} onChange={(e) => setRedirectUri(e.target.value)} required/>
          <input type="text" placeholder="OpenAI Key" value={openAiKey} onChange={(e) => setOpenAiKey(e.target.value)} required/>
          <input type="text" placeholder="YouTube Key" value={youtubeKey} onChange={(e) => setYoutubeKey(e.target.value)} required/>
          {error && <p className="error-message">{error}</p>}
          <button type="submit" className="button button-login">Login with Spotify</button>
        </form>
      </div>
    </div>
  );
};

export default WelcomePage;

