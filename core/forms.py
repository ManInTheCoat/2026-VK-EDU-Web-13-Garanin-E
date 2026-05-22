import os
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, BaseValidator
from core.models import Profile
from django.contrib.auth.forms import AuthenticationForm

class FileSizeValidator(BaseValidator):
    message = 'Размер файла не должен превышать %(limit_value)s МБ.'

    def compare(self, file_obj, limit_mb):
        return file_obj.size > limit_mb * 1024 * 1024

class LoginForm(AuthenticationForm):
    pass

class SignupForm(forms.ModelForm):
    nickname = forms.CharField(label='Nickname', required=True)

    avatar = forms.ImageField(
        label='Profile picture',
        required=False,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            FileSizeValidator(2)
        ]
    )

    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Repeat password')

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match. Please try again.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

            Profile.objects.create(
                user=user,
                nickname=self.cleaned_data.get('nickname'),
                avatar=self.cleaned_data.get('avatar')
            )

        return user

class ProfileForm(forms.ModelForm):
    nickname = forms.CharField(label='Nickname', required=True)

    avatar = forms.ImageField(
        label='Upload new avatar',
        required=False,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            FileSizeValidator(2)
        ]
    )

    class Meta:
        model = User
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['nickname'].initial = self.instance.profile.nickname
            self.fields['avatar'].initial = self.instance.profile.avatar

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            profile = user.profile
            profile.nickname = self.cleaned_data['nickname']
            if self.cleaned_data.get('avatar'):
                profile.avatar = self.cleaned_data['avatar']
            profile.save()

        return user
