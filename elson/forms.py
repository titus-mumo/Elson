from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Audio
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']
        labels = {
            'email': 'Email',
            'username': 'Username',
            'password1': 'Password',
            'password2': 'Confirm Password'
        }



class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        label="Username"
        # widget = forms.CharField(attrs={'placeholder': 'Username', 'autocomplete': 'on'})
    )

    password = forms.CharField(
        max_length=10,
        label='Password',
        widget=forms.PasswordInput(
            attrs={'placeholder': '********', 'autocomplete': 'off'})
    )

    def confirm_validity(self):
        username = self.cleaned_data('username')
        password = self.cleaned_data('password')

        user = authenticate(username=username, password=password)

        if not user or not user.is_active:
            raise forms.ValidationError("Sorry, that login was inactive")

        return self.cleaned_data


class UploadForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100, widget=forms.TextInput(
        attrs={'placeholder': 'Enter title'}))
    description = forms.CharField(label="Description", widget=forms.Textarea(
        attrs={'placeholder': 'Enter description for audio file'}))
    audio = forms.FileField(label="Audio", widget=forms.FileInput(attrs={
                            'class': 'file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700'}))
