from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from django.db import transaction

from django.views import View
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from questions.models import Question, Answer, Tag, QuestionLike, AnswerLike
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

class QuestionLikeAjaxView(View):
    """AJAX обработчик лайков/дизлайков для вопросов"""
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Для оценивания необходимо войти в систему.'}, status=401)

        question_id = request.POST.get('question_id')
        vote_type = request.POST.get('type')

        if vote_type not in ['like', 'dislike']:
            return JsonResponse({'error': 'Неверный тип оценки.'}, status=400)

        question = get_object_or_404(Question, pk=question_id)
        is_like = (vote_type == 'like')

        like_obj, created = QuestionLike.objects.get_or_create(
            user=request.user,
            question=question,
            defaults={'is_like': is_like}
        )

        if not created:
            if like_obj.is_like == is_like:
                like_obj.is_active = not like_obj.is_active
                like_obj.save(update_fields=['is_active'])
            else:
                like_obj.is_like = is_like
                like_obj.is_active = True
                like_obj.save(update_fields=['is_like', 'is_active'])

        likes = QuestionLike.objects.filter(question=question, is_like=True, is_active=True).count()
        dislikes = QuestionLike.objects.filter(question=question, is_like=False, is_active=True).count()
        question.rating = likes - dislikes
        question.save(update_fields=['rating'])

        return JsonResponse({'rating': question.rating})


class AnswerLikeAjaxView(View):
    """AJAX обработчик лайков/дизлайков для ответов"""
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Для оценивания необходимо войти в систему.'}, status=401)

        answer_id = request.POST.get('answer_id')
        vote_type = request.POST.get('type')

        if vote_type not in ['like', 'dislike']:
            return JsonResponse({'error': 'Неверный тип оценки.'}, status=400)

        answer = get_object_or_404(Answer, pk=answer_id)
        is_like = (vote_type == 'like')

        like_obj, created = AnswerLike.objects.get_or_create(
            user=request.user,
            answer=answer,
            defaults={'is_like': is_like}
        )

        if not created:
            if like_obj.is_like == is_like:
                like_obj.is_active = not like_obj.is_active
                like_obj.save(update_fields=['is_active'])
            else:
                like_obj.is_like = is_like
                like_obj.is_active = True
                like_obj.save(update_fields=['is_like', 'is_active'])

        likes = AnswerLike.objects.filter(answer=answer, is_like=True, is_active=True).count()
        dislikes = AnswerLike.objects.filter(answer=answer, is_like=False, is_active=True).count()
        answer.rating = likes - dislikes
        answer.save(update_fields=['rating'])

        return JsonResponse({'rating': answer.rating})


class MarkCorrectAnswerAjaxView(View):
    """AJAX обработчик отметки правильного ответа"""
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Необходимо войти в систему.'}, status=401)

        question_id = request.POST.get('question_id')
        answer_id = request.POST.get('answer_id')

        question = get_object_or_404(Question, pk=question_id)
        answer = get_object_or_404(Answer, pk=answer_id)

        if question.author != request.user:
            return JsonResponse({'error': 'Только автор вопроса может отмечать правильный ответ.'}, status=403)

        if answer.question != question:
            return JsonResponse({'error': 'Этот ответ не относится к данному вопросу.'}, status=400)

        is_currently_correct = answer.is_correct

        with transaction.atomic():
            question.answers.update(is_correct=False)

            if not is_currently_correct:
                answer.is_correct = True
                answer.save(update_fields=['is_correct'])
                status_correct = True
            else:
                status_correct = False

        return JsonResponse({'is_correct': status_correct, 'answer_id': answer.id})
