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
    results = spotify_client.get_top_tracks()

    tracks = []
    for track in results:
        tracks.append({
            'name': track.name,
            'artist': track.artist,
            'id': track.id,
            'album_cover_url': track.album_cover_url
        })

    tracks_dict = get_tracks_dict(tracks)
    return render_template('top_tracks.html', tracks=tracks_dict)


def get_tracks_dict(tracks):
    ai = AI(open_ai_key)
    youtube = Youtube(youtube_key)
    songs = []
    songsInfo = []
    videos_id = []

    #get the video id of the song and chatgpt information of the song
    for index, track in enumerate(tracks): 
        songs.append(f"{track['artist']} {track['name']}")  # Assuming track is an instance of Track class and used to get chatgpt and youtube information
        
        info = ai.generateSongInfo(songs[index])
        info = info.replace('"', '').replace("'", "").replace(":","")
        songsInfo.append(info)

        videos_id.append(youtube.get_video_id(songs[index]))
   
    #could create a database and add this information
    tracks_dict =[
       {
           "track_details": tracks[i],
           "video_id": videos_id[i],
           "info": songsInfo[i]
       }
       for i in range(len(tracks))
    ]
    
    #returns a list of dictionaries which contains the information for each track
    return tracks_dict

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
