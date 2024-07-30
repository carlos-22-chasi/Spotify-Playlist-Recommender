from openai import OpenAI

class AI:
    def __init__(self, api_key_ai):
        self.client = OpenAI(api_key=api_key_ai)
        
    def generateSongInfo(self, song):
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Song with details about artist and song"},
                {"role": "user", "content": f"Tell me about {song}."}
            ]
        )
        return completion.choices[0].message.content