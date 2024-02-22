from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Audio
from django.db import IntegrityError
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from . import views
from . import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import threading
from uuid import uuid4
from .models import Audio, TemporaryAudioFile
from functools import partial
from .templateutils import TemplateRules


@TemplateRules.returns_segment
@csrf_exempt
@login_required
def upload(request):
    if request.method == "POST":
        user = request.user
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
            return TemplateRules.render_html_segment('audio-upload')

        if not audio_file.name.endswith(".mp3"):
            messages.error(request, "File is missing extension")
            return render(request, "audio-segment.html")

        uid = uuid4().hex
        filename = f"{uid}.mp3"
        # server_location = os.path.join(
        #     settings.STATIC_ROOT, "audio", filename)

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
        return TemplateRules.render_html_segment("confirm-details", 
            location = temporary_file.audio_file.url,
            title = title,
            description = description,
            filename = filename,
        )
    
    return render(request, 'elson/sections/audio-upload.html')

@TemplateRules.returns_segment
@csrf_exempt
@login_required
def confirm_audio_file(request):
    print("confirm request")
    # This is htmx triggered so data is always present
    if request.method != "POST":
        messages.error(request, "Bad Request")
        return redirect(views.index)

    upload = request.session.get("upload")
    print(upload)

    if not upload:
        return TemplateRules.render_html_segment("audio-upload")
    user = request.user
    temporary_audio_file_id = upload.get('audio_file_id')
    label = upload.get("label")
    description = upload.get("description")
    filename = upload.get("id")
    uid = upload.get("uid")
    server_location = upload.get('location')
    print(f'uid - {uid}')
    try:
        audio_file = TemporaryAudioFile.objects.get(
            audiofile_id=temporary_audio_file_id)
    except ObjectDoesNotExist:
        audio_file = None
    if audio_file == None:
        messages.error(
            request, "Sorry, you delayed confirmation. Go back to reupload")
        return redirect(views.index)

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
        return TemplateRules.render_html_segment("audio-upload")
    print("here")
    audios = Audio.objects.filter(user = request.user)
    return TemplateRules.render_html_page("index.html", audios=audios)


def delete_file_from_path(file):
    try:
        file_instance = TemporaryAudioFile.objects.filter(
            audiofile_id=file.audiofile_id)
        file_instance.delete()
        print('delete successful')
    except:
        raise ValueError("File doesn't exist")
