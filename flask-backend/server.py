import os
from dotenv import load_dotenv

import urllib.parse
import requests
from flask import Flask, redirect, request, jsonify, session
from flask_cors import CORS
from datetime import datetime

from spotifyclient import SpotifyClient
from openaiGen import AI
from youtubeSearch import Youtube 

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
load_dotenv()

app.secret_key = os.getenv("SECRET_KEY")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

open_ai_key = os.getenv("OPEN_AI_KEY")
youtube_key = os.getenv("YOUTUBE_KEY")

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'



#--------------------------------------functions to login into spotify------------------------------------------------------------------------------------------#
@app.route('/login')
def login():
    print("in login")
    #define the scope of access requested from Spotify
    scope = 'user-read-private user-read-email user-read-recently-played playlist-modify-public user-top-read'
    #construct the authorization URL with the required parameters
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': redirect_uri,
        # 'show_dialog': True  # comment out later if not needed
    }
    #generate the full authorization URL for Spotify
    auth_url = f'{AUTH_URL}?{urllib.parse.urlencode(params)}'
    #redirect the user to the Spotify authorization page
    return redirect(auth_url)

@app.route('/callback')
def callback():
    print("in callback")
    # Check if there is an error in the request arguments
    if 'error' in request.args:
        return jsonify({'error': request.args['error']})
    # Check if the authorization code is in the request arguments
    if 'code' in request.args:
        #prepare the request body to exchange the authorization code for an access token
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }
         #send a POST request to exchange the authorization code for an access token
        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        if response.status_code != 200 or 'access_token' not in token_info:
            return jsonify({'error': 'Failed to retrieve access token', 'response': token_info})
        
        #store the access token and refresh token in the session
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
       
        #get the user id
        url = 'https://api.spotify.com/v1/me'
        headers = {
            'Authorization': f"Bearer {session['access_token']}"
        }
        user_response = requests.get(url, headers=headers)

        #check if the response is successful
        if user_response.status_code != 200:
            return jsonify({'error': 'Failed to fetch user info', 'response': user_response.json()})
    
        #extract and store user information from the response
        user_info = user_response.json()
        session["user_id"] = user_info['id']

        #redirect to the login success page
        return redirect('/login_success')
    
@app.route('/login_success')
#if login is successful it will redirect to the login_successful webpage
def login_success():
    print("in login_success")
    if 'access_token' not in session:
        print("access token not in session")
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        print("access token is expired")
        return redirect('/refresh_token')
    
    return redirect('http://localhost:3000/login_success')

@app.route('/refresh_token')
#refreshes token if it is either expired or no longer in session
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    req_body = {
        'grant_type': 'refresh_token',
        'refresh_token': session['refresh_token'],
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    response = requests.post(TOKEN_URL, data=req_body)
    new_token_info = response.json()

    if response.status_code != 200 or 'access_token' not in new_token_info:
        return jsonify({'error': 'Failed to refresh access token', 'response': new_token_info})

    session['access_token'] = new_token_info['access_token']
    session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

    return redirect('/topTracks')

#--------------------------------------------------------------------------------------------------------------------------------#

@app.route('/topTracks')
def topTracks():
    print("in Top Tracks")

    #check if the user is authenticated by verifying access token or checking if the token is expired
    if 'access_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh_token')
    
    #create an instance of SPotifyClient to interact with the Spotify APi
    spotify_client = SpotifyClient(session["access_token"], session['user_id'])

    #get the top tracks of the spotify user
    top_tracks = spotify_client.get_top_tracks()
    print("main.py: top 5 tracks:")
    for index, track in enumerate(top_tracks):
        print(f"{index+1}- {track}")
   
    # get recommended tracks based off user's top tracks
    recommended_tracks = spotify_client.get_track_recommendations(top_tracks)
    print("main.py: playlist songs:")
    for index, track in enumerate(recommended_tracks):
        print(f"{index+1}- {track}")

    #convert the track objects to dictionaires for json response to buildPlaylistPage.js fetch request
    top_tracks_dicts = [track.to_dict() for track in top_tracks]
    playlist_tracks_dicts = [track.to_dict() for track in recommended_tracks]

    #get additional information for the first recommended track
    extra = get_track_information(recommended_tracks[0])

    #return the top tracks, recommended tracks, and additional track information as JSON
    return jsonify({
        'topTracks': top_tracks_dicts,
        'playlistTracks': playlist_tracks_dicts,
        'extra': extra
    })

def get_track_information(track):
    #create instances of AI and Youtube classes for information retrieval
    ai = AI(open_ai_key)
    youtube = Youtube(youtube_key)

    #get the video id of the song and chatgpt information of the song
    song = f"{track.artist} {track.name}"
    info = ai.generateSongInfo(song)
    # info = info.replace('"', '').replace("'", "").replace(":","") #removes certain characters 
    video_id = youtube.get_video_id(song)
    
    #create a dictionary containing the video ID and track information
    track_details = {"video_id": video_id, "info": info}
    
    #returns details about track in question
    return track_details


@app.route('/getInfo', methods=['POST'])
def get_track_details():
    print("in get track details")
    #parse the JSON request data
    data = request.json
    name = data['name'].strip()
    artist = data['artist'].strip()
    song = f"{name} by {artist}"

    # Check if the song is already in session
    # print("session[song]: ", session[song])

    # if song in session:
    #     print("song is saved in session")
    #     return jsonify(session[song])
    
    # else:
    #   print("song noy in session")
    #create instances of AI and Youtube classes for information retrieval
    ai = AI(open_ai_key)
    youtube = Youtube(youtube_key)

    #get the video id of the song and ChatGPT information of the song
    info = ai.generateSongInfo(song)
    # info = info.replace('"', '').replace("'", "").replace(":", "")
    video_id = youtube.get_video_id(song)

    #create a dictionary containing the video ID and track information
    track_details = {'video_id': video_id, 'info': info}

      # Store the track details in the session
      # session[song] = track_details
      # print("adding to session", session[song])

    return jsonify(track_details)
    
    


@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    #parse the JSON request data
    data = request.json
    name = data.get('name')
    tracks = data.get('tracks')
    
    # print("playlist name: ", name)
    # print("playlist tracks: ", tracks)

    #validate the playlist name
    if not name:
        return jsonify({'success': False, 'error': 'No playlist name provided'}), 400

    try:
        #create an instance of SpotifyClient to interact with the Spotify API
        spotify_client = SpotifyClient(session["access_token"], session['user_id'])

        #create a new playlist and populate it with the provided tracks
        playlist = spotify_client.create_playlist(name)
        response = spotify_client.populate_playlist(playlist, tracks)
        
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        # Return an error response if something goes wrong
        return jsonify({'success': False, 'error': str(e)}), 500




if __name__ == '__main__':
  app.run(debug=True)

