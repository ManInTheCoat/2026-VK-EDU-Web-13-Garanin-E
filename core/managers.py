from django.db import models

class ProfileManager(models.Manager):
    def update_answers_count(self, profile):
        from questions.models import Answer

        count = Answer.objects.filter(author=profile.user).count()
        profile.answers_count = count
        profile.save(update_fields=['answers_count'])
