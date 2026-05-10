from django.shortcuts import render, get_object_or_404
from .models import Question, Tag
from .utils import paginate

def index(request):
    """Список новых вопросов (главная страница)"""
    questions = Question.objects.get_new()
    page = paginate(questions, request, per_page=20)
    return render(request, 'questions/index.html', {'questions': page})

def hot(request):
    """Список лучших вопросов"""
    questions = Question.objects.get_best()
    page = paginate(questions, request, per_page=20)
    return render(request, 'questions/index.html', {'questions': page})

def tag(request, tag_name):
    """Список вопросов по тегу"""
    tag_obj = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.by_tag(tag_obj.id)
    page = paginate(questions, request, per_page=20)
    return render(request, 'questions/index.html', {
        'questions': page,
        'tag_name': tag_obj.name
    })

def question(request, question_id):
    """Страница одного вопроса со списком ответов"""
    one_question = get_object_or_404(Question, pk=question_id, is_active=True)
    answers = one_question.answers.filter(is_active=True).select_related('author', 'author__profile').order_by('-rating', 'created_at')
    page = paginate(answers, request, per_page=30)
    return render(request, 'questions/question.html', {
        'question': one_question,
        'answers': page,
    })

def ask(request):
    """Форма создания вопроса"""
    return render(request, 'questions/ask.html')
