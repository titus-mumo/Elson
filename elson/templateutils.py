import os
from django.shortcuts import redirect, render
from django.urls import reverse


def ensure_required_directories_exists(dirs):
    for k, v in dirs.items():
        print(f"[Log] Initialising {k}", end=" ")
        if os.path.exists(v):
            print(f"{k} found in location: {v}")
        else:
            try:
                print(f"Initializing {k} in location {v}")
                os.makedirs(v)
            except OSError as e:
                print(f"Error {e} occurred")


def login_required(view):
    def wrapped_view(request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("auth:login"))
        return view(request, **kwargs)
    return wrapped_view


class TemplateRules:
    @classmethod
    def render_html_segment(cls, loc, **kwargs):
        loc = loc.rstrip(".html").lstrip("/")
        return render(None, f"elson/sections/{loc}.html", kwargs)

    @classmethod
    def render_html_page(cls, loc, **kwargs):
        loc = loc.replace(".html", "")
        return render(None, f"elson/pages/{loc}.html", kwargs)

    @classmethod
    def returns_segment(cls, func):
        """Just for clarity that this route is used by htmx and returns HTMLSegments"""
        return func

    @classmethod
    def returns_page(cls, func):
        """Just for clarity that this route returns entire HTML pages"""
        return func
