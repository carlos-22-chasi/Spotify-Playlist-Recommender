import React, { useState } from 'react';
import './static/css/PlaylistForm.css';

const PlaylistForm = ({ isVisible, onClose, onSubmit }) => {
  const [playlistName, setPlaylistName] = useState('');

  //handle form submission
  const handleSubmit = (e) => {
    e.preventDefault(); //prevent default form submission behavior
    onSubmit(playlistName); //call onSubmit prop with the playlist name
    setPlaylistName(''); //reset the form
  };
  //ff the form is not visible, render nothing
  if (!isVisible) {
    return null;
  }

  return (
    <div className="form-overlay">
      <div className="form-content">
        <h2>Add Playlist</h2>
        <form onSubmit={handleSubmit}>
          <label>
            Playlist Name:
            <input type="text" value={playlistName} onChange={(e) => setPlaylistName(e.target.value)} required/>
          </label>
          <div className="form-buttons">
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
