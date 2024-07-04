import requests
from track import Track

class SpotifyClient:
    '''
    Purpose:
        performs operation using the Spotify API
    Instance Variables:
        authorization_token (str): Spotify API token
        user_id (str): Spotify user id
    '''

    def __init__(self, authorization_token, user_id):
       self.authorization_token = authorization_token
       self.user_id = user_id

    """
    Gets the top tracks of the user.

    Args:
        limit (int): The maximum number of items that should be contained in the response. Defaults to 10.

    Returns:
        list: A list of Track objects containing the top tracks of the user.
    """
    def get_top_tracks(self, limit=10):
        url = f"https://api.spotify.com/v1/me/top/tracks?limit={limit}"
        response = self._place_get_api_request(url)
        response_json = response.json()
        tracks = [
            Track(
                track["name"],
                track["id"],
                track["artists"][0]["name"],
                track["album"]["images"][0]["url"]
            ) for track in response_json["items"]
        ]
        return tracks
     
    '''
    Makes a GET request to the specified URL with the appropriate headers.
    Args:
        url (str): The URL to make the GET request to.
    Returns:
        requests.Response: The response from the GET request.
    '''
    def _place_get_api_request(self, url):
        response = requests.get(
            url, 
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.authorization_token}"
            }
        )
        return response


