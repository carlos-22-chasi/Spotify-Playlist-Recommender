from openai import OpenAI

class AI:
    '''
    Purpose:
        performs operations using OpenAI API
    Instance Variables:
        client (OpenAI): instance of the OpenAI class fom the openai module
    '''
    def __init__(self, api_key_ai):
        self.client = OpenAI(api_key=api_key_ai)
        
    """
    Purpose:
        Genereate detailed information about a given song using the OpenAI API
    Args:
       song (str>): The name of the song for which to generate information
    Returns:
        str: Detailed information about the song
    """
    def generateSongInfo(self, song):
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Song with details about artist and song"},
                {"role": "user", "content": f"Tell me about {song}."}
            ]
        )
        return completion.choices[0].message.content