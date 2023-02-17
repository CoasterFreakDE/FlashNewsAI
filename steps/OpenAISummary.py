import os
import time

import openai


class OpenAISummary:

    def __init__(self, model, prompt):
        self.model = model
        self.prompt = prompt

    def generate(self):
        openai.organization = os.getenv("OPENAI_ORGANIZATION")
        openai.api_key = os.getenv("OPENAI_API_KEY")

        start_time = time.time()

        response = openai.Completion.create(
            model=self.model,
            prompt=self.prompt,
            temperature=1,
            max_tokens=1000,
            stream=True,
        )

        # create variables to collect the stream of events
        collected_events = []
        completion_text = ''
        # iterate through the stream of events
        for event in response:
            event_time = time.time() - start_time  # calculate the time delay of the event
            collected_events.append(event)  # save the event response
            event_text = event['choices'][0]['text']  # extract the text
            completion_text += event_text  # append the text
            print(f"Text received: {event_text} ({event_time:.2f} seconds after request)")  # print the delay and text

        # print the time delay and text received
        print(f"Full response received {event_time:.2f} seconds after request")
        print(f"Full text received: {completion_text}")
        return completion_text
