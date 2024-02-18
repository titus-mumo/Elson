from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload, name='upload'),
    path('confirm-audio-file/', views.confirm_audio_file, name='confirm_audio_file'),
    path('home/', views.home, name='home')
]
