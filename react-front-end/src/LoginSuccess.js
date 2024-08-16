import React, { useEffect } from 'react';
import './static/css/LoginSuccess.css'; // Make sure to create this CSS file

const LoginSuccessPage = () => {
  useEffect(() => {
    const fetchData = async () => {
      try {
        //fetch top tracks and playlist tracks from the backend
        const response = await fetch('http://localhost:5000/topTracks', {
          credentials: 'include'
        }); 
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();

       //store data in local storage
       localStorage.setItem('topTracks', JSON.stringify(data.topTracks));
       localStorage.setItem('playlistTracks', JSON.stringify(data.playlistTracks));
       localStorage.setItem('extra', JSON.stringify(data.extra));

        //redirect after fetching data
        window.location.href = '/build_playlist';
      
      } catch (error) {
        console.error('Fetch error:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="login-container">
      <h1>Login Successful</h1>
      <p>You have successfully logged in with Spotify.</p>
      <p>Currently loading in data ...</p>
    </div>
  );
};

export default LoginSuccessPage;
