from django.db import models

class TagManager(models.Manager):
    def update_questions_count(self, tag):
        count = tag.questions.filter(is_active=True).count()
        tag.questions_count = count
        tag.save(update_fields=['questions_count'])

class QuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related('author', 'author__profile').prefetch_related('tags')

    def get_new(self):
        return self.get_queryset().filter(is_active=True).order_by('-created_at')

    def get_best(self):
        return self.get_queryset().filter(is_active=True).order_by('-rating', '-created_at')

    def by_tag(self, tag_id):
        return self.get_queryset().filter(tags__id=tag_id, is_active=True).order_by('-created_at')

    def update_answers_count(self, question):
        count = question.answers.filter(is_active=True).count()
        question.answers_count = count
        question.save(update_fields=['answers_count'])
