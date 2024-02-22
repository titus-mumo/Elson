from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .templateutils import TemplateRules
from .models import Audio


@TemplateRules.returns_page
@csrf_exempt
@login_required
def index(request):
    audios = Audio.objects.filter(user=request.user)
    return TemplateRules.render_html_page("index.html", audios=audios)
