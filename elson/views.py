from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Audio
from django.db import IntegrityError
from django.shortcuts import render

# Create your views here.

from . import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import shutil
import os
import threading
from uuid import uuid4
from .models import Audio, User, TemporaryAudioFile
from django.conf import settings
from .transcriber import utils as trascriberutils
from functools import partial


@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect(login_view)
        else:
            print(form.errors)
            messages.error(request, "Unsuccessful registration.")
    else:
        form = forms.RegisterForm()
    return render(request, 'elson/register.html', {'form': form})


@csrf_exempt
def login_view(request):
    if request.method == 'GET':
        form = forms.LoginForm
        return render(request, 'elson/login.html', {'form': form})
    else:
        form = forms.LoginForm(request.POST)
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You have successfully logged in")
                return redirect(upload)
            else:
                form = forms.LoginForm()
                messages.error(request, "Invalid username or password")
                return render(request, 'elson/login.html', {'form': form})
        else:
            form = forms.LoginForm()
            messages.error(request, "Invalid username or password")
            return render(request, 'elson/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully")
    return redirect('login')


@login_required
def upload(request):
    if request.method == "POST":
        user = request.user
        print(type(user))
        title = request.POST.get("title")
        label = title
        description = request.POST.get("description")
        print(description)
        audio_file = request.FILES.get("audio")
        if not title:
            messages.error(request, "Audio file title is required")
        if not description:
            messages.error(request, "Please add description for audio file")
        if not audio_file:
            messages.error(request, "Audio file is required")

        if not title or not description or not audio_file:
            form = forms.UploadForm
            return render(request, 'elson/upload.html', {'form': form})
        if Audio.objects.filter(user=user, label=label).exists():
            messages.error(request, "Label provided has been used before")
            # Render with pre-filled data
            form = forms.UploadForm
            return render(request, 'elson/upload.html', {'form': form})

        if not audio_file.name.endswith(".mp3"):
            messages.error(request, "File is missing extension")
            return render(request, "audio-segment.html")

        uid = uuid4().hex
        filename = f"{uid}.mp3"
        # server_location = os.path.join(
        #     settings.MEDIA_ROOT, "audio", filename)

        # # Create the directory if it doesn't exist
        # os.makedirs(os.path.dirname(server_location), exist_ok=True)

        temporary_file = TemporaryAudioFile.objects.create(
            audio_file=audio_file)

        # with open(server_location, 'wb+') as destination:
        #     for chunk in audio_file.chunks():
        #         destination.write(chunk)

        # Remove the audio file after 5 min on a separate thread
        def remove_file():
            try:
                threading.Timer(
                    60.0 * 5, partial(delete_file_from_path, temporary_file)).start()
            except Exception as e:
                print("Error while removing file:", e)

        remove_file()

        request.session["upload"] = {
            "id": filename,
            "label": title,
            "description": description,
            "uid": uid,
            "audio_file_id": temporary_file.audiofile_id,
        }

        print(str(request.session))

        print(temporary_file.audio_file.url)
        return render(request, "elson/confirm-details.html", {
            "location": temporary_file.audio_file.url,
            "title": title,
            "description": description,
            "filename": filename,
        })
    else:
        form = forms.UploadForm
    return render(request, 'elson/upload.html', {'form': form})


@login_required
def confirm_audio_file(request):
    print("confimr request")
    # This is htmx triggered so data is always present
    if request.method != "POST":
        return HttpResponseBadRequest("Bad request")

    upload = request.session.get("upload")
    print(upload)

    if not upload:
        return render(request, "audio/audio-upload.html")
    user = request.user
    temporary_audio_file_id = upload.get('audio_file_id')
    label = upload.get("label")
    description = upload.get("description")
    filename = upload.get("id")
    uid = upload.get("uid")
    server_location = upload.get('location')
    print(f'uid - {uid}')
    if not temporary_audio_file_id:
        messages.error(
            request, "Sorry, you delayed confirmation. Go back to reupload")
        return render(request, "audio/audio-upload.html")

    audio_file = TemporaryAudioFile.objects.get(audiofile_id = temporary_audio_file_id)
    print(audio_file.audio_file.url)
    # Cancel pending threads (if any)
    # pending_threads[server_location].cancel()
    # pending_threads.pop(server_location)

    print("executed_audio_file")

    try:
        # Save the audio details to the database
        audio = Audio.objects.create(
            label=label,
            description=description,
            user=user,
            audio_file=audio_file.audio_file,
            uid=uid,
            length=20,
            # trascriberutils.get_audio_file_length_in_secs(audio_file.audio_file.url)
            uploaded_at=timezone.now()
        )
        messages.success(request, "Audio uploaded successfully 💾")
    except IntegrityError as ie:
        messages.error(request, "Sorry something went wrong")
        print(ie)
        return render(request, "audio/audio-upload.html")

    # Fetch all audios for the current user
    audios = Audio.objects.filter(user=user)

    return render(request, "elson/left-nav.html", {"audios": audios})


def delete_file_from_path(file):
    try:
        TemporaryAudioFile.objects.delete(file)
    except:
        raise ValueError("File doesn't exist")
    
def home(request):
    return render(request, 'elson/home.html')
