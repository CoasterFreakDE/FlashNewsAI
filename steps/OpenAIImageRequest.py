import os
import time

import fade
from openai import OpenAI


class OpenAIImageRequest:

    def __init__(self, prompt):
        self.prompt = prompt
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    def generate(self):
        start_time = time.time()

        response = self.client.images.generate(
            prompt=self.prompt,
            model="dall-e-3",
            style="vivid",
            quality="hd",
            n=1,
            size='1024x1792'
        )

        end_time = time.time()
        duration = end_time - start_time
        
        print(fade.greenblue(f"Image generated in {duration:.2f} seconds"))

        return response.data[0].url

        
        

       
