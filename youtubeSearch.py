import googleapiclient.discovery

class Youtube:
    def __init__(self, api_key):
        self.client = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)

    def get_video_id(self, video_name):
        request = self.client.search().list(
            part="snippet",
            q=video_name,
            maxResults=1,
            type="video",
            videoEmbeddable="true"
        )
        response = request.execute()
        video_id = response['items'][0]['id']['videoId']
        return video_id

    