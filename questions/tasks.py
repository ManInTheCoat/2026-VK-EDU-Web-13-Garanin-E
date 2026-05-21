from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum, F, Q
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from django.conf import settings
from cent import Client, PublishRequest
from django.core.mail import send_mail

from questions.models import Tag, Question, Answer

@shared_task
def update_popular_tags_cache():
    """Считает 10 тегов с самым большим числом вопросов за последние 3 месяца"""
    three_months_ago = timezone.now() - timedelta(days=90)

    popular_tags = list(Tag.objects.filter(
        questions__created_at__gte=three_months_ago
    ).annotate(
        q_count=Count('questions')
    ).order_by('-q_count')[:10])

    cache.set('popular_tags', popular_tags, timeout=60 * 60)
    return f"Updated popular tags cache: {len(popular_tags)} tags"

@shared_task
def update_best_users_cache():
    """Считает 10 пользователей по рейтингу вопросов/ответов за последнюю неделю"""
    one_week_ago = timezone.now() - timedelta(days=7)

    best_users = list(User.objects.annotate(
        q_rating=Coalesce(Sum('questions__rating', filter=Q(questions__created_at__gte=one_week_ago)), 0),
        a_rating=Coalesce(Sum('answers__rating', filter=Q(answers__created_at__gte=one_week_ago)), 0)
    ).annotate(
        total_rating=F('q_rating') + F('a_rating')
    ).filter(total_rating__gt=0).order_by('-total_rating')[:10])

    cache.set('best_users', best_users, timeout=60 * 60)
    return f"Updated best users cache: {len(best_users)} users"

@shared_task
def send_new_answer_notification(question_id, answer_id):
    """Отправляет уведомление о новом ответе в Centrifugo"""
    client = Client(settings.CENTRIFUGO_URL, api_key=settings.CENTRIFUGO_API_KEY, timeout=1)

    data = {
        'answer_id': answer_id
    }
    channel = f"questions:{question_id}"

    request = PublishRequest(channel=channel, data=data)
    client.publish(request)

    return f"Sent ping for answer {answer_id} to {channel}"

@shared_task
def send_email_notification_task(question_id, answer_id):
    """Отправляет email-уведомление автору вопроса"""
    try:
        question = Question.objects.get(id=question_id)
        answer = Answer.objects.get(id=answer_id)
    except (Question.DoesNotExist, Answer.DoesNotExist):
        return f"Question {question_id} or Answer {answer_id} not found."

    author = question.author

    if not author.email:
        return f"User {author.username} has no email address."

    if author == answer.author:
        return "Author answered their own question. Email skipped."

    subject = f"Новый ответ на ваш вопрос: {question.title}"
    message = (
        f"Здравствуйте, {author.username}!\n\n"
        f"На ваш вопрос '{question.title}' только что ответили.\n\n"
        f"Текст ответа:\n{answer.text}\n\n"
        f"С уважением,\nКоманда Nice Answer"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[author.email],
        fail_silently=False,
    )

    return f"Email notification sent to {author.email}"
