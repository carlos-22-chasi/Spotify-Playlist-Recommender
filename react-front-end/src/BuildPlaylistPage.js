// src/BuildPlaylist.js
import React, { useEffect, useState } from 'react';
import './static/css/BuildPlaylistPage.css'; 
import PlaylistForm from './PlaylistForm';

const BuildPlaylist = () => {
   //state hooks for managing top tracks, playlist tracks, current track details, and form visibility
  const [topTracks, setTopTracks] = useState([]);
  const [playlistTracks, setPlaylistTracks] = useState([]);
  const [currentTrackDetails, setCurrentTrackDetails] = useState({ video_id: '', info: '' });
  const [isPlaylistFormVisible, setIsPlaylistFormVisible] = useState(false);

  useEffect(() => {
    //retrieve data from local storage
    const storedTopTracks = JSON.parse(localStorage.getItem('topTracks'));
    const storedPlaylistTracks = JSON.parse(localStorage.getItem('playlistTracks'));
    const storedExtra = JSON.parse(localStorage.getItem('extra'));

    //set data 
    if (storedTopTracks) setTopTracks(storedTopTracks);
    if (storedPlaylistTracks) setPlaylistTracks(storedPlaylistTracks);
    if (storedExtra) setCurrentTrackDetails(storedExtra);
  }, []);

  //function to show song details when a song is clicked
  const showSongDetails = async (name, artist) => {
    //create a unique key based on song details
    const songKey = `${name} by ${artist}`; 

    // check local storage for cached song details
    const cachedData = localStorage.getItem(songKey);
    
    if (cachedData) {
      // If cached data exists, parse and use it
      setCurrentTrackDetails(JSON.parse(cachedData));
      console.log("song was cached")
      return;
    }
    
    try {
      //fetch song details from the backend
      const response = await fetch('http://localhost:5000/getInfo', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, artist }),
      });
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      //update the state with fetched data
      const trackDetails = await response.json();
      setCurrentTrackDetails(trackDetails)
      localStorage.setItem(songKey, JSON.stringify(trackDetails));
    } catch (error) {
      console.error('Error fetching track details:', error);
    }
  };

  //function to show the playlist submission form 
  const showPopup = () => {
    setIsPlaylistFormVisible(true)
  };

  //function to handle closing the form
  const handlePlaylistFormClose = () => {
    setIsPlaylistFormVisible(false);
  };

  //function to handle form submission
  const handleFormSubmit = async (playlistName) => {
    try {
      //fetch response to see if playlist was created succesffuly 
      const response = await fetch('http://localhost:5000/create_playlist', {
        credentials: 'include',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: playlistName, tracks: playlistTracks }),
      });
      const result = await response.json();
      if (result.success) {
        alert('Playlist created successfully!');
      } else {
        alert(`Failed to create playlist: ${result.error}`);
      }
    } catch (error) {
      console.error('Error creating playlist:', error);
      alert('An error occurred while creating the playlist.');
    } finally {
      setIsPlaylistFormVisible(false);
    }
  };

  return (
    <div className="container">
      <div className="left">
        <p>Your Top 5 Songs</p>
        <div className="top-tracks">
          {topTracks.map((track, index) => (
            <div className="song" key={index} onClick={() => showSongDetails(track.name, track.artist)}>
              <div className="rank">
                <p>{index + 1}.</p>
              </div>
              <div className="title">
                <p>{track.name} by {track.artist}</p>
              </div>
              <div className="albumCover">
                <img src={track.album_cover_url} alt={track.name} />
              </div>
            </div>
          ))}
        </div>
        <p>Created Suggested Playlist</p>
        <div className="new-playlist-songs">
          {playlistTracks.map((track, index) => (
            <div className="song" key={index} onClick={() => showSongDetails(track.name, track.artist)}>
              <div className="rank">
                <p>{index + 1}.</p>
              </div>
              <div className="title">
                <p>{track.name} by {track.artist}</p>
              </div>
              <div className="albumCover">
                <img src={track.album_cover_url} alt={track.name} />
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="right">
        {
          <>
            <div className="video-container">
              <iframe
                src={`https://www.youtube.com/embed/${currentTrackDetails.video_id}?&autoplay=1&mute=1`}
                frameBorder="0"
                allowFullScreen
                title="YouTube video"
              ></iframe>
            </div>
            <div className="information">
              <p>{currentTrackDetails.info}</p>
            </div>
            <div className="add-playlist">
              <p>Would you like to add the playlist to your account?</p>
              <button onClick={showPopup}>Add Playlist</button>
            </div>
          </>
        }
      </div>
      <PlaylistForm
        isVisible={isPlaylistFormVisible}
        onClose={handlePlaylistFormClose}
        onSubmit={handleFormSubmit}
      />
    </div>
  );
};

export default BuildPlaylist;
