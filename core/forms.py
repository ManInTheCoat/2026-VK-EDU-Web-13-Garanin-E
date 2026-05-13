from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from core.models import Profile
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    pass

class SignupForm(forms.ModelForm):
    nickname = forms.CharField(label='Nickname', required=True)
    avatar = forms.ImageField(label='Profile picture', required=False)

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
    avatar = forms.ImageField(label='Upload new avatar', required=False)

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
