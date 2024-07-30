import os
from dotenv import load_dotenv

import urllib.parse
import requests
from flask import Flask, redirect, request, jsonify, session, url_for, render_template
from datetime import datetime

from spotifyclient import SpotifyClient
from openaiGen import AI
from youtubeSearch import Youtube  # Add this line to import the Youtube class

import googleapiclient.discovery
from openai import OpenAI

from jinja2 import Template

app = Flask(__name__)

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

@app.route('/')
def index():
    return render_template('welcome_page.html')

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email user-read-recently-played playlist-modify-public user-top-read'
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': redirect_uri,
        # 'show_dialog': True  # comment out later if not needed
    }
    auth_url = f'{AUTH_URL}?{urllib.parse.urlencode(params)}'
    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({'error': request.args['error']})
    
    if 'code' in request.args:
        #get the access token and other important information
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }
        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        if response.status_code != 200 or 'access_token' not in token_info:
            return jsonify({'error': 'Failed to retrieve access token', 'response': token_info})
        
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
       
        #get the user id
        url = 'https://api.spotify.com/v1/me'
        headers = {
            'Authorization': f"Bearer {session['access_token']}"
        }
        user_response = requests.get(url, headers=headers)
        if user_response.status_code != 200:
            return jsonify({'error': 'Failed to fetch user info', 'response': user_response.json()})
    
        user_info = user_response.json()
        session["user_id"] = user_info['id']

        return redirect('/login_success')
    
@app.route('/login_success')
def login_success():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh_token')
        
    return render_template('login_success.html')

@app.route('/topTracks')
def topTracks():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh_token')
    
    spotify_client = SpotifyClient(session["access_token"], session['user_id'])
    top_tracks = spotify_client.get_top_tracks()

    print("main.py: top 5 tracks:")
    for index, track in enumerate(top_tracks):
        print(f"{index+1}- {track}")

   
    # get recommended tracks based off user's top tracks
    recommended_tracks = spotify_client.get_track_recommendations(top_tracks)
    print("main.py: playlist songs:")
    for index, track in enumerate(recommended_tracks):
        print(f"{index+1}- {track}")

    return render_template('top_tracks.html', top_tracks=top_tracks, playlist_tracks = recommended_tracks)

'''////////////////////////////////////////////////////////////////////////////////////////////////////////////////////'''
def get_track_information(track):
    ai = AI(open_ai_key)
    youtube = Youtube(youtube_key)

    #get the video id of the song and chatgpt information of the song
    song = f"{track['artist']} {track['name']}" # Assuming track is an instance of Track class and used to get chatgpt and youtube information
    info = ai.generateSongInfo(song)
    info = info.replace('"', '').replace("'", "").replace(":","") #removes certain characters 
    video_id = youtube.get_video_id(song)
   
    #could create a database and add this information
    track_details =[
       {
           "video_id": video_id,
           "info": info
       }
    ]
    
    #returns details about track in question
    return track_details
'''////////////////////////////////////////////////////////////////////////////////////////////////////////////////////'''

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({'success': False, 'error': 'No playlist name provided'}), 400

    try:
        playlist = spotify_client.create_playlist(name)
        # Assuming you have a function to get the tracks
        tracks = get_tracks_somehow()
        response = spotify_client.populate_playlist(playlist, tracks)
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/refresh_token')
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
