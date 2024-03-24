import os
from pydub import AudioSegment
from django.conf import settings

# TODO: Support most audio formats


def get_audio_file_length_in_secs(file_path: str) -> int:
    """Get length of mp3 files in sec"""

    print("file_path")
    print(file_path)
    audio_path = file_path.replace('\\', '/')
    absolute_path = os.path.abspath(audio_path)
    
    if not os.path.exists(absolute_path):
        raise FileExistsError()
    else:
        print('ok..processing')
    audio: AudioSegment = AudioSegment.from_mp3(absolute_path)
    return int(audio.duration_seconds)
