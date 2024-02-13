from django.shortcuts import render

# Create your views here.

from . import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect(login_view)
        else:
            messages.error(request, "Unsuccessful registration.")
    else:
        form = forms.RegisterForm()
    return render(request, 'app/register.html', {'form': form})


@csrf_exempt
def login_view(request):
    if request.method == 'GET':
        form = forms.LoginForm
        return render(request, 'app/login.html', {'form': form})
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
            return render(request, 'app/login.html', {'form': form})


@login_required
def upload():
    pass


def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully")
    return redirect('login')
