import os
from pydub import AudioSegment
from django.conf import settings

# TODO: Support most audio formats


def get_audio_file_length_in_secs(loc: str) -> int:
    """Get length of mp3 files in sec"""

    media_root_parent = os.path.dirname(settings.STATIC_ROOT)
    path = media_root_parent + loc
    file_path = os.path.normpath(path)
    print(file_path)
    print("hello")
    if not os.path.exists(file_path):
        raise FileExistsError()
    else:
        print('ok..processing')

    audio: AudioSegment = AudioSegment.from_file(file_path)
    return int(audio.duration_seconds)
