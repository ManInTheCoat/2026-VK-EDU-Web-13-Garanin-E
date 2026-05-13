from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from questions.models import Question, Answer, Tag

class QuestionForm(forms.ModelForm):
    tags_input = forms.CharField(label='Tags', required=True, help_text='Введите теги через запятую')

    class Meta:
        model = Question
        fields = ['title', 'text']

    def clean_tags_input(self):
        tags_string = self.cleaned_data.get('tags_input', '')

        tag_names = [tag.strip() for tag in tags_string.split(',') if tag.strip()]

        if not tag_names:
            raise ValidationError("Please provide at least one valid tag.")

        if len(tag_names) > 3:
            raise ValidationError("You can add a maximum of 3 tags.")

        return tags_string

    def save(self, commit=True, author=None):
        question = super().save(commit=False)

        question.author = author

        if commit:
            with transaction.atomic():
                question.save()

                tags_string = self.cleaned_data.get('tags_input', '')
                if tags_string:
                    tag_names = [tag.strip() for tag in tags_string.split(',') if tag.strip()]
                    for name in tag_names:
                        tag_obj, created = Tag.objects.get_or_create(name=name)
                        question.tags.add(tag_obj)

        return question

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']

    def save(self, commit=True, author=None, question=None):
        answer = super().save(commit=False)

        answer.author = author
        answer.question = question

        if commit:
            answer.save()

        return answer
