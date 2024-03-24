from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import User
from django.db import IntegrityError
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from . import views

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
from django.conf import settings
from .transcriber import utils as trascriberutils
from functools import partial
from .templateutils import TemplateRules


@csrf_exempt
@TemplateRules.returns_page
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        email = request.POST.get('email', None)
        confirm_password = request.POST.get("confirm-password", None)
        passwords_identical = password == confirm_password

        if not passwords_identical:
            messages.error(request, "Passwords do not match")
        if not username:
            messages.error(request, "Username is required")
        elif not password:
            messages.error(request, "Password is required")
        elif not email:
            messages.error(request, "Email is required")
        if passwords_identical and username and password and email:
            try:
                user = User()
                user.email = email
                user.username = username
                user.set_password(password)
                user.save()
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                messages.success(request, "Registration successful.")
                return redirect(login_view)
            except IntegrityError as ie:
                messages.error(request, "Unsuccessful registration.")
                print(ie)
    return TemplateRules.render_html_page("auth.html", login=False)


@csrf_exempt
@TemplateRules.returns_page
def login_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect(views.index)
        else:
            return TemplateRules.render_html_page("auth.html", login=True)
    else:
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You have successfully logged in")
                return redirect(views.index)
            else:
                messages.error(request, "Invalid username or password")
                return TemplateRules.render_html_page("auth.html", login=True)
        else:
            messages.error(request, "Invalid username or password")
            return TemplateRules.render_html_page("auth.html", login=True)


@login_required
def logout_view(request):
    try:
        logout(request)
        messages.info(request, "Logged out successfully")
    except:
        messages.info(request, "You were not logged in")
    return redirect('login')


def auth(request):
    return render(request, 'elson/pages/auth.html')

def handle_unmatching_urls(request):
    if request.user.is_authenticated:
        return redirect(views.index)
    else:
        return redirect(login_view)
