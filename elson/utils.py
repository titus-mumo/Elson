from dataclasses import dataclass
from threading import Timer
from .models import User


def stop_timer(t: Timer):
    if t.finished:
        return
    t.cancel()


@dataclass
class AudioDiagnosticsFile:
    uid: str


class AudioUploadException(Exception):
    def __init__(self, user: User, *args) -> None:
        super().__init__(*args)


class ConfirmedAudioFileExists(AudioUploadException):
    def __init__(self, user: User, file_details: AudioDiagnosticsFile) -> None:
        # Log the information
        super().__init__(user)
