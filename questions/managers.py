from django.db import models

class QuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related('author', 'author__profile').prefetch_related('tags')

    def get_new(self):
        return self.get_queryset().order_by('-created_at')

    def get_best(self):
        return self.get_queryset().order_by('-rating', '-created_at')

    def by_tag(self, tag_name):
        return self.get_queryset().filter(tags__name=tag_name).order_by('-created_at')
