function showSongDetails(video_id, song_info){
  let videoContainer = document.querySelector('.video-container iframe');
  let infoContainer = document.querySelector('.bottom p');
  
  videoContainer.src = `https://www.youtube.com/embed/${video_id}?&autoplay=1&mute=1`;
  infoContainer.textContent = song_info;
  
}