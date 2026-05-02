from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F
from questions.models import Answer
from .models import Profile

@receiver(post_save, sender=Answer)
def increment_answers_count(sender, instance, created, **kwargs):
    """
    Срабатывает, когда создается новый ответ. Увеличивает счетчик профиля.
    """
    if created and hasattr(instance.author, 'profile'):
        profile = instance.author.profile
        profile.answers_count = F('answers_count') + 1
        profile.save(update_fields=['answers_count'])

@receiver(post_delete, sender=Answer)
def decrement_answers_count(sender, instance, **kwargs):
    """
    Срабатывает, когда ответ удаляется. Уменьшает счетчик профиля.
    """
    if hasattr(instance.author, 'profile'):
        profile = instance.author.profile
        profile.answers_count = F('answers_count') - 1
        profile.save(update_fields=['answers_count'])
