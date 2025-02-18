import json
import os
import random
import shutil
from uuid import uuid4

import dotenv
import fade
import urllib

from steps.OpenAIImageRequest import OpenAIImageRequest
from steps.ElevenLabsTTS import ElevenLabsTTS
from steps.OpenAIRequest import OpenAIRequest
from steps.TranscriptionAI import TranscriptionAI
from steps.VideoCreation import VideoCreation
from steps.YoutubeUploader import YoutubeUploader

dotenv.load_dotenv()

answers = list(os.getenv("OPTIONS"))

if __name__ == '__main__':
    print(
        fade.greenblue("""
⣱⣿⣿⡟⡐⣰⣧⡷⣿⣴⣧⣤⣼⣯⢸⡿⠁⣰⠟⢀⣼⠏⣲⠏⢸⣿⡟⣿⣿⣿⣿⣿⣿
⣿⣿⡟⠁⠄⠟⣁⠄⢡⣿⣿⣿⣿⣿⣿⣦⣼⢟⢀⡼⠃⡹⠃⡀⢸⡿⢸⣿⣿⣿⣿⣿⡟
⣿⣿⠃⠄⢀⣾⠋⠓⢰⣿⣿⣿⣿⣿⣿⠿⣿⣿⣾⣅⢔⣕⡇⡇⡼⢁⣿⣿⣿⣿⣿⣿⢣
⣿⡟⠄⠄⣾⣇⠷⣢⣿⣿⣿⣿⣿⣿⣿⣭⣀⡈⠙⢿⣿⣿⡇⡧⢁⣾⣿⣿⣿⣿⣿⢏⣾      Welcome to unexplained phenomena of our universe!
⣿⡇⠄⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢻⠇⠄⠄⢿⣿⡇⢡⣾⣿⣿⣿⣿⣿⣏⣼⣿      A project by @CoasterFreakDE
⣿⣷⢰⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⢰⣧⣀⡄⢀⠘⡿⣰⣿⣿⣿⣿⣿⣿⠟⣼⣿⣿
⢹⣿⢸⣿⣿⠟⠻⢿⣿⣿⣿⣿⣿⣿⣿⣶⣭⣉⣤⣿⢈⣼⣿⣿⣿⣿⣿⣿⠏⣾⣹⣿⣿    This project is licensed under the GPL3 License.
⢸⠇⡜⣿⡟⠄⠄⠄⠈⠙⣿⣿⣿⣿⣿⣿⣿⣿⠟⣱⣻⣿⣿⣿⣿⣿⠟⠁⢳⠃⣿⣿⣿
⠄⣰⡗⠹⣿⣄⠄⠄⠄⢀⣿⣿⣿⣿⣿⣿⠟⣅⣥⣿⣿⣿⣿⠿⠋⠄⠄⣾⡌⢠⣿⡿⠃
⠜⠋⢠⣷⢻⣿⣿⣶⣾⣿⣿⣿⣿⠿⣛⣥⣾⣿⠿⠟⠛⠉⠄⠄
        """)
    )
    listen = ''
    if len(answers) < 1:
        print(fade.greenblue('Do you want to start now? (y/N)'))
        listen = input()
    else:
        listen = answers[0]
    if listen != 'y':
        print(fade.greenblue('Exiting...'))
        exit(0)

    print(fade.greenblue('Generating video script...'))
    print("" if len(os.getenv('STORY_OVERRIDE')) < 1 else fade.greenblue('Using story override: ' + os.getenv('STORY_OVERRIDE')))
    print("" if len(os.getenv('TOPIC_OVERRIDE')) < 1 else fade.greenblue('Using topic override: ' + os.getenv('TOPIC_OVERRIDE')))
    
    
    story_topic = "Over the past centuries, there were many unexplained buildings and phenomena in our universe" if len(os.getenv('TOPIC_OVERRIDE')) < 1 else os.getenv('TOPIC_OVERRIDE')
    
    
    # Generate a topic, that was not used before (save topics to a file)
    used_topics = []
    try:
        with open('topics.txt', 'r', encoding='utf-8') as f:
            for line in f:
                used_topics.append(line.strip())
    except FileNotFoundError:
        pass
            
    topic = OpenAIRequest(os.getenv("OPENAI_MODEL"), f"""
            Generate a topic for {story_topic}. The topic should be something that is not used before. 

            Do not use the following topics (we used them before):
            {used_topics}

            """).generate()
                
    with open('topics.txt', 'a', encoding='utf-8') as f:
        f.write(f"{topic}\n")
    
    print(fade.greenblue(f'Topic: {topic}'))
    
    ai_output = OpenAIRequest(os.getenv("OPENAI_MODEL"), f"""
I want you to act as a storyteller. 

{"Write a script for a 30-60 second video script (only what I need to speak) about {topic}. Please also include information, that are not proven and just possible explanations." if len(os.getenv('STORY_OVERRIDE')) < 1 else os.getenv('STORY_OVERRIDE')}

Just write the script. No introducing sentence. Start directly with the text, I need to say.
Start with: “Welcome to our exploration of the unexplained phenomena of our universe”.
    """).generate()

    yt_information = OpenAIRequest(os.getenv("OPENAI_MODEL"),
                                   "Generate a catching youtube title and description (seperated by @) without"
                                   " formatting for the following video script: " + ai_output).generate()

    yt_title = yt_information.split('@')[0]
    yt_description = yt_information.split('@')[1]

    print(fade.greenblue('Title: ' + yt_title))
    print(fade.greenblue('Description: ' + yt_description))
    
    print(fade.greenblue('Generating images...'))
    image_prompts = OpenAIRequest(os.getenv("OPENAI_MODEL"),
                                   f"""Generate a list of image prompts (one image for each sentence) as detailed as possible in the style of
                                   {os.getenv("IMAGE_STYLE")} (mention the style in each prompt),
                                   Separate the prompts by '@'!
                                   
                                   This is the full video script:
                                   
                                   {ai_output}
                                   
                                   If there are characters in the story, describe their main features the same in all prompts.
                                   """).generate()
    
    prompts = image_prompts.split('@')
    print(fade.greenblue(f'Generating {len(prompts)} images...'))
    image_urls = []
    for prompt in prompts:
        if len(prompt) < 1:
            continue
        print(fade.greenblue(f"Prompt: {prompt}"))
        image_url = OpenAIImageRequest(prompt).generate()
        image_urls.append(image_url)
        print(fade.greenblue(f"Image URL: {image_url}"))
        

    print(fade.greenblue('Generating audio file...'))
    eleven_labs_vid = os.getenv("ELEVEN_LABS_VOICE_ID")
    with open('voices.json', encoding='utf-8') as f:
        voices = json.load(f)
    if eleven_labs_vid == "RANDOM":
        eleven_labs_vid = random.choice(list(voices.keys()))

    selected_voice = voices[eleven_labs_vid]
    print(fade.greenblue('Selected voice: ' + selected_voice['name']))

    uuid = str(uuid4())

    audio_file = ElevenLabsTTS(ai_output, uuid, eleven_labs_vid, selected_voice).generate()
    if audio_file is None:
        print(fade.fire('Error generating audio file.'))
    export = ''
    if len(answers) < 2:
        print(fade.greenblue('Do you want to export the files (e) or automatically generate the video (A)?'))
        export = input()
    else:
        export = answers[1]
    if export == 'e':
        print(fade.greenblue('Exporting files...'))
        with open('output/output_' + uuid + '.txt', 'w', encoding='utf-8') as f:
            f.write(ai_output)

        shutil.copyfile(audio_file, 'output/output_' + uuid + '.mp3')
        
        index = 0
        for image_url in image_urls:
            target_path = os.path.join('output', 'output_' + uuid + "_" + str(index) + '.png')
            urllib.request.urlretrieve(image_url, target_path)
            index += 1

        print(fade.greenblue('Files exported.'))
        exit(0)

    transcript_steps, spoken_sentences = TranscriptionAI(audio_file).transcribe()
    print(fade.greenblue('Transcript generated.'))
    print(fade.greenblue('Generating video...'))
    VideoCreation(audio_file, transcript_steps, spoken_sentences).generate()
    print(fade.greenblue('Video generated.'))

    upload = ''
    if len(answers) < 3:
        print(fade.greenblue('Do you want to upload the video (u)?'))
        upload = input()
    else:
        upload = answers[2]
    if upload == 'u':
        print(fade.greenblue('Uploading video...'))
        yt = YoutubeUploader('output.mp4', yt_title, yt_description).upload()
        print(fade.greenblue('Video uploaded.'))
