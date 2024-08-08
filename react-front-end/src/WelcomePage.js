// src/WelcomePage.js
import React from 'react';
import './static/css/WelcomePage.css';
import logo from './static/images/spotify-logo.jpg';

const WelcomePage = () => {
  const handleLogin = () => {
    window.location.href = 'http://localhost:5000/login';
  };

  return (
    <div>
      <div className="logo-container">
        <img src={logo} alt="Spotify Logo" className="logo" />
      </div>
      <div className="container">
        <h1>Welcome to My Spotify App</h1>
        <button onClick={handleLogin} className="button button-login">Login with Spotify</button>
      </div>
    </div>
  );
};

export default WelcomePage;

