import os
import uuid
from django.db import models
from django.contrib.auth.models import User
from core.managers import ProfileManager
from django.templatetags.static import static

def avatar_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('avatars/', new_filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
    avatar = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True, verbose_name='Аватар')
    nickname = models.CharField(max_length=255, blank=True, verbose_name='Никнейм')
    answers_count = models.IntegerField(default=0)

    objects = ProfileManager()

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return self.user.username

    @property
    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        return static('img/default_avatar.jpg')
