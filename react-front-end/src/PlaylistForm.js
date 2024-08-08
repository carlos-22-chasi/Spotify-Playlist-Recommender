import React, { useState } from 'react';
import './static/css/PlaylistForm.css';

const PlaylistForm = ({ isVisible, onClose, onSubmit }) => {
  const [playlistName, setPlaylistName] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(playlistName);
    setPlaylistName(''); // Reset the form
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Add Playlist</h2>
        <form onSubmit={handleSubmit}>
          <label>
            Playlist Name:
            <input
              type="text"
              value={playlistName}
              onChange={(e) => setPlaylistName(e.target.value)}
              required
            />
          </label>
          <div className="modal-buttons">
            <button type="submit">Submit</button>
            <button type="button" onClick={onClose}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PlaylistForm;
