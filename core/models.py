from django.db import models
from django.contrib.auth.models import User
from .managers import ProfileManager

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Аватар')
    nickname = models.CharField(max_length=255, blank=True, verbose_name='Никнейм')
    answers_count = models.IntegerField(default=0)

    objects = ProfileManager()

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return self.user.username
