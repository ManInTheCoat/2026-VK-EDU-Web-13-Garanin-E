from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from questions.managers import TagManager, QuestionManager

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector

class DefaultModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_active = models.BooleanField(default=True, verbose_name='Активно?')

    class Meta:
        abstract = True

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название тега')
    questions_count = models.IntegerField(default=0)

    objects = TagManager()

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

class Question(DefaultModel):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    text = models.TextField(max_length=4000, verbose_name='Текст вопроса')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='questions', verbose_name='Автор')
    tags = models.ManyToManyField(Tag, related_name='questions', verbose_name='Теги')
    rating = models.IntegerField(default=0, db_index=True, verbose_name='Рейтинг')
    answers_count = models.IntegerField(default=0)

    objects = QuestionManager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-rating', '-created_at']),
            GinIndex(
                SearchVector('title', 'text', config='english'),
                name='question_search_idx'
            )
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('question', kwargs={'question_id': self.pk})

class Answer(DefaultModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Вопрос')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='answers', verbose_name='Автор')
    text = models.TextField(max_length=4000, verbose_name='Текст ответа')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный ответ?')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Ответ на вопрос #{self.question_id} пользователя #{self.author_id}'

class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='likes', verbose_name='Вопрос')
    is_like = models.BooleanField(default=True, verbose_name='Лайк?')
    is_active = models.BooleanField(default=True, verbose_name='Активно?')

    class Meta:
        unique_together = ('user', 'question')
        verbose_name = 'Лайк к вопросу'
        verbose_name_plural = 'Лайки к вопросам'

class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes', verbose_name='Ответ')
    is_like = models.BooleanField(default=True, verbose_name='Лайк?')
    is_active = models.BooleanField(default=True, verbose_name='Активно?')

    class Meta:
        unique_together = ('user', 'answer')
        verbose_name = 'Лайк к ответу'
        verbose_name_plural = 'Лайки к ответам'
