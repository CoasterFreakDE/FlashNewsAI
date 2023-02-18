import datetime

import fade
from moviepy.editor import *


class VideoCreation:

    def __init__(self, audio_file, transcript_steps, sentences):
        self.audio_file = audio_file
        self.sentences = sentences
        self.transcript_steps: [] = transcript_steps

    def generate(self):
        video_duration = timestamp_from_str(self.transcript_steps[-1]["timestamp_end"])
        total_seconds = min(video_duration.second + 2, 60)
        print(fade.greenblue(f"Total video time: {total_seconds}"))

        clip = VideoFileClip("assets/background.mp4").subclip(0, total_seconds)
        background_audio = clip.audio
        background_audio = background_audio.volumex(0.12)
        audio_composition = CompositeAudioClip([AudioFileClip(self.audio_file), background_audio])
        clip = clip.set_audio(audio_composition)

        texts = []
        sentence_index = 0
        current_sentence = ''
        for i in range(len(self.transcript_steps)):
            span_text = self.transcript_steps[i]["span_text"]
            if current_sentence == self.sentences[sentence_index]:
                sentence_index += 1
                current_sentence = ''
            current_sentence += span_text

            if span_text == "." or span_text == "," or span_text == " " or span_text == "  ":
                continue
            start_time = timestamp_from_str(self.transcript_steps[i]["timestamp"])
            end_time = timestamp_from_str(self.transcript_steps[i]["timestamp_end"])
            step_duration = end_time - start_time

            text_clip = TextClip(span_text, fontsize=50, color='white')
            text_clip = text_clip.set_start(start_time.second + start_time.microsecond / 1000000)

            # As duration, we need to calculate the difference between the start and the start of the next step
            if i < len(self.transcript_steps) - 1:
                next_step_start_time = timestamp_from_str(self.transcript_steps[i + 1]["timestamp"])
                real_step_duration = next_step_start_time - start_time
                text_clip = text_clip.set_duration(real_step_duration.seconds + real_step_duration.microseconds / 1000000)
            else:
                text_clip = text_clip.set_duration(step_duration.seconds + step_duration.microseconds / 1000000)

            text_clip = text_clip.set_position('center')

            texts.append(text_clip)

        # Overlay the text clip on the first video clip
        video = CompositeVideoClip([clip] + texts)

        # Write the result to a file (many options available !)
        video.write_videofile(".temp/output.mp4", fps=30, codec="libx264", audio_codec="aac",
                              threads=4, preset="ultrafast", ffmpeg_params=["-ac", "1"])
        ffmpeg_tools.ffmpeg_extract_subclip(
            ".temp/output.mp4", 0, total_seconds, targetname=f"output.mp4"
        )


def timestamp_from_str(timestamp):
    return datetime.datetime.strptime(timestamp, "%H:%M:%S.%f")
