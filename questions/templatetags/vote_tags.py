from django import template

register = template.Library()

@register.simple_tag
def get_question_vote(likes_map, question):
    """Возвращает статус лайка из заранее собранного словаря: 'like', 'dislike' или 'none'"""
    if not likes_map:
        return 'none'

    is_like = likes_map.get(question.id)
    if is_like is True:
        return 'like'
    elif is_like is False:
        return 'dislike'

    return 'none'

@register.simple_tag
def get_answer_vote(likes_map, answer):
    """Возвращает статус лайка из заранее собранного словаря: 'like', 'dislike' или 'none'"""
    if not likes_map:
        return 'none'

    is_like = likes_map.get(answer.id)
    if is_like is True:
        return 'like'
    elif is_like is False:
        return 'dislike'

    return 'none'
