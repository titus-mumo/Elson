from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from datetime import datetime

# Create your models here.


class Base(models.Model):
    date_added = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now_add=True)

    @property
    def date_added(self):
        return self.date_added.strftime("%m/%d%Y")

    @date_added.setter
    def date_added(self, date: datetime):
        self.date_added = date

    @property
    def last_modified(self):
        return self.last_modified.strftime("%m/%d%Y")

    @last_modified.setter
    def last_modified(self, date: datetime):
        self.last_modified = date


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=email,
            username=username,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    user_id = models.AutoField(unique=True, primary_key=True)
    email = models.CharField(max_length=40, unique=True)
    username = models.CharField(max_length=40, unique=True)
    # password = models.CharField(max_length=128)  # Storing hashed passwords

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class TemporaryAudioFile(models.Model):
    audiofile_id = models.AutoField(primary_key=True, unique=True)
    audio_file = models.FileField(upload_to='temporary/')

    def __str__(self):
        # Convert to string to represent the file path
        return str(self.audio_file)

    def get_audio_file(self):
        """
        Method to return the audio file content.
        """
        try:
            with open(self.audio_file.path, 'rb') as file:
                return file.read()
        except FileNotFoundError:
            print("No file found")
            return None  # Handle file not found error

class Audio(models.Model):
    audio_id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='audio/', null=True)
    label = models.CharField(max_length=30)
    uid = models.CharField(max_length = 50, null=True)
    description = models.CharField(max_length=200)
    _length = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add = True, null = True)

    @property
    def length(self) -> str:
        h = int(self._length // 3600)
        m = int(self._length // 60)
        s = int(self._length % 60)

        return "".join(
            [
                f"{h} Hrs " if h > 0 else "",
                f"{m} Min " if m > 0 else "",
                f"{s} Secs" if s > 0 else "",
            ]
        )

    @length.setter
    def length(self, length: int) -> None:
        # length in seconds
        self._length = length

    def __str__(self) -> str:
        return f"Audio {self.label}"


class Transcription(models.Model):
    transcription_id = models.AutoField(primary_key=True, unique=True)
    value = models.CharField(max_length=100000)
    audio = models.ForeignKey(Audio, on_delete=models.CASCADE)



