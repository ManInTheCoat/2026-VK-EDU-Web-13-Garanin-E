from django.db.models.signals import m2m_changed, post_save, post_delete
from django.dispatch import receiver
from django.db.models import F
from .models import Question, Tag, Answer

@receiver(m2m_changed, sender=Question.tags.through)
def update_tags_count(sender, instance, action, pk_set, **kwargs):
    """
    Срабатывает при добавлении или удалении тегов у вопроса.
    """
    if action == "post_add":
        Tag.objects.filter(pk__in=pk_set).update(questions_count=F('questions_count') + 1)
    elif action == "post_remove":
        Tag.objects.filter(pk__in=pk_set).update(questions_count=F('questions_count') - 1)

@receiver(post_save, sender=Answer)
def increment_question_answers_count(sender, instance, created, **kwargs):
    """Срабатывает при создании ответа: обновляет счетчик у самого вопроса."""
    if created:
        Question.objects.filter(pk=instance.question_id).update(answers_count=F('answers_count') + 1)

@receiver(post_delete, sender=Answer)
def decrement_question_answers_count(sender, instance, **kwargs):
    """Срабатывает при удалении ответа: уменьшает счетчик у самого вопроса."""
    Question.objects.filter(pk=instance.question_id).update(answers_count=F('answers_count') - 1)
