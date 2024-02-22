from django.urls import path
from . import views, audio, auth, upload

urlpatterns = [
    path('', auth.login_view, name='login'),
    path('register/', auth.register, name='register'),
    path('logout/', auth.logout_view, name='logout'),
    path('upload/', upload.upload, name='upload'),
    path('confirm-audio-file/', upload.confirm_audio_file,
         name='confirm_audio_file'),
    path('index/', views.index, name='index'),
    path('generate/<str:uid>', audio.generate, name='generate'),
    path('audio/<str:uid>', audio.open_audio, name='audio'),
    path('auth/', auth.auth, name='auth'),
    path('player/<str:uid>', audio.player, name='player')
]
