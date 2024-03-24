from elson import auth
from django.shortcuts import redirect

def initialize(request):
    return redirect(auth.login_view)

def error_handling(request):
    return redirect(auth.login_view)