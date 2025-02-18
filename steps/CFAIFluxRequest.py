import base64
import os
import time

import fade
import requests


class CFAIFluxRequest:

    def __init__(self, prompt):
        self.prompt = prompt

    def generate(self):
        start_time = time.time()

        response = requests.post(
            url=f"https://api.cloudflare.com/client/v4/accounts/{os.environ.get('CLOUDFLARE_ACCOUNT_ID')}/ai/run/@cf/black-forest-labs/flux-1-schnell",
            headers={
                "Authorization": f"Bearer {os.environ.get('CLOUDFLARE_API_KEY')}",
            },
            json={
                "prompt": self.prompt,
            },
            timeout=30,
        )

        end_time = time.time()
        duration = end_time - start_time
        
        try:
            result = response.json()
            if result['success'] != True:
                print(fade.fire(f"CloudFlareAI Flux failed: {result['status']}"))
                return None
        
            base64_image = response.json()['result']['image']
        
            image_bytes = base64.b64decode(base64_image)
            
            print(fade.greenblue(f"Image generated in {duration:.2f} seconds"))

            return image_bytes
        except Exception as e:
            print(fade.fire(f"Error: {e} in {result}"))
            return None

        
        

       
