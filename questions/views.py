from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy

from django.views import View
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from questions.models import Question, Tag
from questions.utils import paginate
from questions.forms import QuestionForm, AnswerForm

class IndexView(ListView):
    """Список новых вопросов (главная страница)"""
    template_name = 'questions/index.html'

    def get_queryset(self):
        return Question.objects.get_new()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = paginate(self.object_list, self.request, per_page=20)
        return context

class HotQuestionsView(ListView):
    """Список лучших вопросов"""
    template_name = 'questions/index.html'

    def get_queryset(self):
        return Question.objects.get_best()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = paginate(self.object_list, self.request, per_page=20)
        return context

class TagQuestionsView(ListView):
    """Список вопросов по тегу"""
    template_name = 'questions/index.html'

    def get_queryset(self):
        self.tag_obj = get_object_or_404(Tag, name=self.kwargs['tag_name'])
        return Question.objects.by_tag(self.tag_obj.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag_name'] = self.tag_obj.name
        context['questions'] = paginate(self.object_list, self.request, per_page=20)
        return context

class QuestionDetailView(View):
    """Страница одного вопроса со списком ответов и формой добавления ответа"""

    def get(self, request, question_id, *args, **kwargs):
        one_question = get_object_or_404(Question, pk=question_id, is_active=True)
        answers = one_question.answers.filter(is_active=True).select_related('author', 'author__profile').order_by('-rating', 'created_at')

        form = AnswerForm()

        return render(request, 'questions/question.html', {
            'question': one_question,
            'answers': answers,
            'form': form,
        })

    def post(self, request, question_id, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")

        one_question = get_object_or_404(Question, pk=question_id, is_active=True)
        form = AnswerForm(request.POST)

        if form.is_valid():
            answer = form.save(author=request.user, question=one_question)

            redirect_url = f"{reverse('question', args=[one_question.id])}#answer-{answer.id}"
            return redirect(redirect_url)

        answers = one_question.answers.filter(is_active=True).select_related('author', 'author__profile').order_by('-rating', 'created_at')

        return render(request, 'questions/question.html', {
            'question': one_question,
            'answers': answers,
            'form': form,
        })

class AskQuestionView(LoginRequiredMixin, CreateView):
    """Форма создания вопроса"""
    template_name = 'questions/ask.html'
    form_class = QuestionForm

    def form_valid(self, form):
        new_question = form.save(author=self.request.user)
        return redirect('question', question_id=new_question.id)
