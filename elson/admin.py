from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'email', 'username', 'is_active', 'is_admin', )
    search_fields = ('email', 'username', )
    list_filter = ('username', )

@admin.register(models.Audio)
class AudioAdmin(admin.ModelAdmin):
    list_display = ('audio_id', 'user', 'audio_file', 'label', 'uid', 'description', '_length', 'uploaded_at')

@admin.register(models.TemporaryAudioFile)
class AudioAdmin(admin.ModelAdmin):
    list_display = ('audiofile_id', 'audio_file',)
