from django.contrib import admin
from questions.models import Question, Answer, Tag, QuestionLike, AnswerLike

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    raw_id_fields = ["author"]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "created_at", "rating"]
    search_fields = ["title", "text", "author__username"]
    list_filter = ["created_at", "tags"]
    inlines = [AnswerInline]

    raw_id_fields = ["author"]
    list_select_related = ["author"]

    filter_horizontal = ["tags"]

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ["short_text", "question", "author", "created_at", "is_correct", "rating"]
    search_fields = ["text", "author__username", "question__title"]
    list_filter = ["is_correct", "created_at"]

    raw_id_fields = ["question", "author"]
    list_select_related = ["question", "author"]

    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    short_text.short_description = "Текст ответа"

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]

@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ["user", "question", "is_like"]
    raw_id_fields = ["user", "question"]
    list_select_related = ["user", "question"]

@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ["user", "answer", "is_like"]
    raw_id_fields = ["user", "answer"]
    list_select_related = ["user", "answer"]
