from datetime import datetime

import fade
from moviepy.editor import *

class VideoCreation:

    def __init__(self, audio_file, transcript_steps):
        self.audio_file = audio_file
        self.transcript_steps: [] = transcript_steps

    def generate(self):
        video_duration = timestamp_from_str(self.transcript_steps[-1]["timestamp_end"])
        total_seconds = video_duration.second + 2
        print(fade.greenblue(f"Total video time: {total_seconds}"))

        clip = VideoFileClip("assets/background.mp4").subclip(0, total_seconds)
        clip = clip.set_audio(AudioFileClip(self.audio_file))

        for step in self.transcript_steps:
            start_time = timestamp_from_str(step["timestamp"])
            end_time = timestamp_from_str(step["timestamp_end"])
            step_duration = end_time - start_time
            step_duration_seconds = step_duration.seconds + 1
            text_clip = TextClip(step["span_text"], fontsize=70, color='white')
            text_clip = text_clip.set_duration(step_duration_seconds)
            text_clip = text_clip.set_position('center').set_start(start_time.second)

            clip = CompositeVideoClip([clip, text_clip])

        # Overlay the text clip on the first video clip
        video = CompositeVideoClip([clip])

        # Write the result to a file (many options available !)
        video.write_videofile(".temp/output.mp4", fps=30, codec="libx264", audio_codec="aac", audio_bitrate="192k",
                              threads=4, preset="ultrafast")
        ffmpeg_tools.ffmpeg_extract_subclip(
            ".temp/output.mp4", 0, total_seconds, targetname=f"output.mp4"
        )


def timestamp_from_str(timestamp):
    return datetime.strptime(timestamp, "%H:%M:%S.%f")
