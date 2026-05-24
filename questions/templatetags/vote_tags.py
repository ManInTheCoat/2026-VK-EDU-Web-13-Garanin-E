from django import template
from questions.models import QuestionLike, AnswerLike

register = template.Library()

@register.simple_tag
def get_question_vote(user, question):
    """Возвращает статус лайка пользователя для вопроса: 'like', 'dislike' или 'none'"""
    if not user or not user.is_authenticated:
        return 'none'

    vote = QuestionLike.objects.filter(user=user, question=question, is_active=True).first()

    if vote:
        return 'like' if vote.is_like else 'dislike'
    return 'none'

@register.simple_tag
def get_answer_vote(user, answer):
    """Возвращает статус лайка пользователя для ответа: 'like', 'dislike' или 'none'"""
    if not user or not user.is_authenticated:
        return 'none'

    vote = AnswerLike.objects.filter(user=user, answer=answer, is_active=True).first()

    if vote:
        return 'like' if vote.is_like else 'dislike'
    return 'none'
