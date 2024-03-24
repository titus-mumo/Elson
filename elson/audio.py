# Create your views here.

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Audio, Transcription
from .templateutils import TemplateRules
from .tools.audio_splitter import TimebasedAudioSplitter
from .transcriber.transcriber import Transcriber
from .models import Audio
from django.db import IntegrityError
import os
from django.conf import settings

transcriber = Transcriber()
working_directory = os.getcwd()


@login_required
@TemplateRules.returns_segment
@csrf_exempt
def open_audio(request, uid:str):
    if request.method == "POST":
        return "Wrong method requested", 400
    user = request.user
    audio_queryset = Audio.objects.filter(uid = uid).filter(user = user)
    audio = audio_queryset.first()
    if not audio or audio.user != user:
        # TODO: Add further logging
        messages.error(request, "Something went wrong")
        return TemplateRules.render_html_segment("right-nav"), 500
    return TemplateRules.render_html_segment("right-nav", audio = audio)

@login_required
@csrf_exempt
@TemplateRules.returns_segment
def generate(request, uid: str):
    print(uid)
    if request.method == "POST":
        return "Wrong method", 400
    user = request.user
    audio_queryset = Audio.objects.filter(uid = uid).filter(user = user)
    audio = audio_queryset.first()
    if not audio or audio.user != user:
        messages.error("Something went wrong")
        return TemplateRules.render_html_segment("right-nav")
    audio_file = str(audio.audio_file)
    audio_loc = os.path.join(str(settings.MEDIA_ROOT), audio_file.replace('/', '\\'))
    print(f"Path, {audio_loc}")
    #TODO: The function below results to an error
    audio_splitter = TimebasedAudioSplitter(audio_loc, 10)
    try:
        print("Executing this line")
        transcription = Transcription.objects.create(value = transcriber.transcribe(audio_splitter), audio = audio)
    except IntegrityError as ie:
        messages.error(request, "Sorry something went wrong")
        print(ie)
        return TemplateRules.render_html_segment("right-nav")
    
    return TemplateRules.render_html_segment(
        "right-nav", audio=audio, transacription = transcription
    )

@login_required
@csrf_exempt
def player(request, uid: str):
    if request.method == "POST":
        return "Wrong request", 400
    user = request.user
    audio_queryset = Audio.objects.filter(uid = uid).filter(user = user)
    audio = audio_queryset.first()
    if not audio:
        messages.error(request, "Something went wrong")
        return "<p>Error</p>", 400
    if audio.user != user:
        messages.error(request, "Something went wrong")
        return "<p>Error</p>", 401
    
    return TemplateRules.render_html_segment(
        "audio-player", location = audio.audio_file.url
    )


