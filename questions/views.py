import math
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Question, Tag
from .utils import paginate
from .forms import QuestionForm, AnswerForm

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
    """Страница одного вопроса со списком ответов и формой добавления ответа"""
    one_question = get_object_or_404(Question, pk=question_id, is_active=True)
    answers = one_question.answers.filter(is_active=True).select_related('author', 'author__profile').order_by('-rating', 'created_at')

    ANSWERS_PER_PAGE = 30

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")

        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(author=request.user, question=one_question)

            ordered_answer_ids = list(
                one_question.answers.filter(is_active=True)
                .order_by('-rating', 'created_at')
                .values_list('id', flat=True)
            )

            answer_index = ordered_answer_ids.index(answer.id)

            last_page = (answer_index // ANSWERS_PER_PAGE) + 1

            redirect_url = f"{reverse('question', args=[one_question.id])}?page={last_page}#answer-{answer.id}"
            return redirect(redirect_url)
    else:
        form = AnswerForm()

    page = paginate(answers, request, per_page=ANSWERS_PER_PAGE)

    return render(request, 'questions/question.html', {
        'question': one_question,
        'answers': page,
        'form': form,
    })

@login_required(login_url='login')
def ask(request):
    """Форма создания вопроса"""
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            new_question = form.save(author=request.user)

            return redirect('question', question_id=new_question.id)
    else:
        form = QuestionForm()

    return render(request, 'questions/ask.html', {'form': form})
