import React, { useEffect } from 'react';
import './static/css/LoginSuccess.css'; // Make sure to create this CSS file

const LoginSuccessPage = () => {
  useEffect(() => {
    // Redirect to the backend login route after 3 seconds
    const timer = setTimeout(() => {
      window.location.href = '/build_playlist';
    }, 3000);

    // Clean up timer if the component is unmounted
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="container">
      <h1>Login Successful</h1>
      <p>You have successfully logged in with Spotify.</p>
      <p>Currently loading in data ...</p>
    </div>
  );
};

export default LoginSuccessPage;
