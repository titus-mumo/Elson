from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Audio
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(
        attrs={'autocomplete': 'off', 'data-toggle': 'password'}))
    password2 = forms.CharField(
        label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']
        labels = {
            'user_email': 'User Email',
            'username': 'Username',
            'password1': 'Password',
            'password2': 'Confirm Password'
        }

    def clean_email(self):
        user_email = self.cleaned_data.get('user_email')
        if User.objects.filter(user_email=user_email).exists():
            raise forms.ValidationError(
                "This email address is already registered.")

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username allready exists.")

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2


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
