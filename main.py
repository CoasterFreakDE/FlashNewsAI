import json
import os
import random
import shutil

import dotenv
import fade

from steps.CFAIFluxRequest import CFAIFluxRequest
from steps.ElevenLabsTTS import ElevenLabsTTS
from steps.OpenAIRequest import OpenAIRequest
from steps.TranscriptionAI import TranscriptionAI
from steps.VideoCreation import VideoCreation
from steps.YoutubeUploader import YoutubeUploader

dotenv.load_dotenv()

answers = list(os.getenv("OPTIONS"))

def sanitize_filename(filename: str) -> str:
    # Replace invalid filename characters with underscores
    import re
    # Remove quotes and replace other invalid characters with underscore
    return re.sub(r'[<>:"/\\|?*\']', '_', filename.replace('"', '').replace("'", "")).replace(' ', '_')

if __name__ == '__main__':
    print(
        fade.greenblue("""
⣱⣿⣿⡟⡐⣰⣧⡷⣿⣴⣧⣤⣼⣯⢸⡿⠁⣰⠟⢀⣼⠏⣲⠏⢸⣿⡟⣿⣿⣿⣿⣿⣿
⣿⣿⡟⠁⠄⠟⣁⠄⢡⣿⣿⣿⣿⣿⣿⣦⣼⢟⢀⡼⠃⡹⠃⡀⢸⡿⢸⣿⣿⣿⣿⣿⡟
⣿⣿⠃⠄⢀⣾⠋⠓⢰⣿⣿⣿⣿⣿⣿⠿⣿⣿⣾⣅⢔⣕⡇⡇⡼⢁⣿⣿⣿⣿⣿⣿⢣
⣿⡟⠄⠄⣾⣇⠷⣢⣿⣿⣿⣿⣿⣿⣿⣭⣀⡈⠙⢿⣿⣿⡇⡧⢁⣾⣿⣿⣿⣿⣿⢏⣾      Welcome to FlashNewsAI!
⣿⡇⠄⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢻⠇⠄⠄⢿⣿⡇⢡⣾⣿⣿⣿⣿⣿⣏⣼⣿      A project by @LiamXSage
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
    
    
    story_topic = "A fake news story that could be published on television."
    
    # Generate a topic, that was not used before (save topics to a file)
    used_topics = []
    try:
        with open('topics.txt', 'r', encoding='utf-8') as f:
            for line in f:
                used_topics.append(line.strip())
    except FileNotFoundError:
        pass
            
    topic = OpenAIRequest(os.getenv("OPENAI_MODEL"), f"""
            Generate a precise/specific topic about the following:
            
            {story_topic}
            
            ---
        
            The topic should be something that is not used before.
            Keep the topic short and concise. (1-4 words)

            Do not use the following topics (we used them before):
            {used_topics}

            """).generate()
    
    topic_named = sanitize_filename(topic.lower())
    
    # create topic folder
    os.makedirs(f'output/{topic_named}', exist_ok=True)
                
    with open('topics.txt', 'a', encoding='utf-8') as f:
        f.write(f"{topic}\n")
    
    print(fade.greenblue(f'Topic: {topic}'))
    
    ai_output = OpenAIRequest(os.getenv("OPENAI_MODEL"), f"""
        You are a news reporter.
        I want you to discuss {topic}.
        
        Tell it as if you were speaking about it at a television news report, drawing in your audience until the end.
        Always begin with some scroll-stopping hook such as "This unsolved mystery has people baffled."
        or "You won't believe what happened to [insert person here]."
        or "Try not to panic, ..." etc. these are just examples, but I want it to draw in your listener.
        
        Try to make the story as interesting as possible, but also make it believable.
        Keep the story short and to the point, but complete. (6-12 sentences)
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
                                   f"""Generate a list of image prompts (2-5 images for each sentence, whenever it makes sense) as detailed as possible in the style of
                                   {os.getenv("IMAGE_STYLE")} (mention the style in each prompt),
                                   Separate the prompts by '\n'!
                                   
                                   This is the full video script:
                                   
                                   {ai_output}
                                   
                                   If there are characters in the story, describe their main features the same in all prompts.
                                   """).generate()
    
    prompts = image_prompts.split('\n')
    print(fade.greenblue(f'Generating {len(prompts)} images...'))
    image_bytes_list = []
    for prompt in prompts:
        if len(prompt) <= 5:
            continue
        print(fade.greenblue(f"Prompt: {prompt}"))
        image_bytes = CFAIFluxRequest(prompt).generate()
        if image_bytes is None:
            pass
        image_bytes_list.append(image_bytes)
        

    print(fade.greenblue('Generating audio file...'))
    eleven_labs_vid = os.getenv("ELEVEN_LABS_VOICE_ID")
    with open('voices.json', encoding='utf-8') as f:
        voices = json.load(f)
    if eleven_labs_vid == "RANDOM":
        eleven_labs_vid = random.choice(list(voices.keys()))

    selected_voice = voices[eleven_labs_vid]
    print(fade.greenblue('Selected voice: ' + selected_voice['name']))

   

    audio_file = ElevenLabsTTS(ai_output, topic_named, eleven_labs_vid, selected_voice).generate()
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
        with open(f'output/{topic_named}/script' + '.txt', 'w', encoding='utf-8') as f:
            f.write(ai_output)

        shutil.copyfile(audio_file, f'output/{topic_named}/voiceover' + '.mp3')
        
        index = 0
        for image_bytes in image_bytes_list:
            try:
                target_path = os.path.join(f'output/{topic_named}', 'image_' + str(index) + '.png')
                with open(target_path, 'wb') as f:
                    f.write(image_bytes)
                index += 1
            except Exception as e:
                print(fade.fire(f'Error exporting image {index}: {e}'))

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
