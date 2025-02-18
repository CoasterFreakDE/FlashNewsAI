import os
import time

import fade
from openai import OpenAI


class OpenAIRequest:

    def __init__(self, model, prompt):
        self.model = model
        self.prompt = prompt
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    def generate(self):
        start_time = time.time()

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompt}
            ],
            temperature=1,
            max_completion_tokens=1000,
            stream=True,
        )

        # create variables to collect the stream of events
        collected_events = []
        completion_text = ""
        # iterate through the stream of events
        for chunk in stream:
            event_time = time.time() - start_time  # calculate the time delay of the event
            collected_events.append(chunk)  # save the event response
            event_text = chunk.choices[0].delta.content or ""
            completion_text += event_text  # append the text

        # print the time delay and text received
        print(fade.greenblue(f"Full response received {event_time:.2f} seconds after request"))
        return completion_text
