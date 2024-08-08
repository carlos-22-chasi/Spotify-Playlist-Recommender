// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import WelcomePage from './WelcomePage';
import LoginSuccess from './LoginSuccess';
import BuildPlaylistPage from './BuildPlaylistPage'; // Ensure this component exists
import './static/css/App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<WelcomePage />} />
        <Route path="/login_success" element={<LoginSuccess />} />
        <Route path="/build_playlist" element={<BuildPlaylistPage />} />
      </Routes>
    </Router>
  );
}

export default App;
