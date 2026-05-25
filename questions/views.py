from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse

from django.views import View
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from questions.models import Question, Answer, Tag, QuestionLike, AnswerLike
from questions.forms import QuestionForm, AnswerForm
from questions.tasks import send_new_answer_notification, send_email_notification_task
from questions.utils import get_centrifugo_data

class ElidedPaginationMixin:
    """
    Примесь для добавления красивой пагинации с многоточием (...).
    Вычисляет диапазон страниц и кладет его прямо в нативный page_obj.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = context.get('page_obj')
        if page is not None:
            page.custom_page_range = page.paginator.get_elided_page_range(
                page.number, on_each_side=2, on_ends=1
            )
        return context

class QuestionLikesContextMixin:
    """
    Добавляет в контекст словарь 'question_likes_map'.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            questions = context.get('object_list', [])
            question_ids = [q.id for q in questions]

            likes_qs = QuestionLike.objects.filter(
                user=self.request.user,
                question_id__in=question_ids,
                is_active=True
            )
            context['question_likes_map'] = {like.question_id: like.is_like for like in likes_qs}
        else:
            context['question_likes_map'] = {}

        return context


class LoginRequiredApiMixin:
    """
    Примесь для AJAX-представлений.
    Перехватывает запрос в методе dispatch, и если пользователь не авторизован,
    возвращает JSON с 401 кодом.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Необходимо войти в систему.'}, status=401)
        return super().dispatch(request, *args, **kwargs)


class IndexView(QuestionLikesContextMixin, ElidedPaginationMixin, ListView):
    """Список новых вопросов (главная страница)"""
    template_name = 'questions/index.html'
    paginate_by = 20
    context_object_name = 'questions'

    def get_queryset(self):
        return Question.objects.get_new()


class HotQuestionsView(QuestionLikesContextMixin, ElidedPaginationMixin, ListView):
    """Список лучших вопросов"""
    template_name = 'questions/index.html'
    paginate_by = 20
    context_object_name = 'questions'

    def get_queryset(self):
        return Question.objects.get_best()


class TagQuestionsView(QuestionLikesContextMixin, ElidedPaginationMixin, ListView):
    """Список вопросов по тегу"""
    template_name = 'questions/index.html'
    paginate_by = 20
    context_object_name = 'questions'

    def get_queryset(self):
        self.tag_obj = get_object_or_404(Tag, name=self.kwargs['tag_name'])
        return Question.objects.by_tag(self.tag_obj.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag_name'] = self.tag_obj.name
        return context


class QuestionDetailView(View):
    """Страница одного вопроса со списком ответов и формой добавления ответа"""

    def get(self, request, question_id, *args, **kwargs):
        one_question = get_object_or_404(Question, pk=question_id, is_active=True)
        answers = one_question.answers.filter(is_active=True).select_related('author', 'author__profile').order_by('-rating', 'created_at')
        form = AnswerForm()

        question_likes_map = {}
        answer_likes_map = {}

        if request.user.is_authenticated:
            q_like = QuestionLike.objects.filter(user=request.user, question_id=one_question.id, is_active=True).first()
            if q_like:
                question_likes_map[one_question.id] = q_like.is_like

            answer_ids = [a.id for a in answers]
            a_likes_qs = AnswerLike.objects.filter(user=request.user, answer_id__in=answer_ids, is_active=True)
            answer_likes_map = {like.answer_id: like.is_like for like in a_likes_qs}

        context = {
            'question': one_question,
            'answers': answers,
            'form': form,
            'question_likes_map': question_likes_map,
            'answer_likes_map': answer_likes_map,
        }
        context.update(get_centrifugo_data(request))

        return render(request, 'questions/question.html', context)

    def post(self, request, question_id, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")

        one_question = get_object_or_404(Question, pk=question_id, is_active=True)
        form = AnswerForm(request.POST)

        if form.is_valid():
            answer = form.save(author=request.user, question=one_question)
            one_question.sync_answers_count()
            send_new_answer_notification.delay(one_question.id, answer.id)
            send_email_notification_task.delay(one_question.id, answer.id)
            redirect_url = f"{reverse('question', args=[one_question.id])}#answer-{answer.id}"
            return redirect(redirect_url)

        answers = one_question.answers.filter(is_active=True).select_related('author', 'author__profile').order_by('-rating', 'created_at')

        question_likes_map = {}
        answer_likes_map = {}

        if request.user.is_authenticated:
            q_like = QuestionLike.objects.filter(user=request.user, question_id=one_question.id, is_active=True).first()
            if q_like:
                question_likes_map[one_question.id] = q_like.is_like

            answer_ids = [a.id for a in answers]
            a_likes_qs = AnswerLike.objects.filter(user=request.user, answer_id__in=answer_ids, is_active=True)
            answer_likes_map = {like.answer_id: like.is_like for like in a_likes_qs}

        context = {
            'question': one_question,
            'answers': answers,
            'form': form,
            'question_likes_map': question_likes_map,
            'answer_likes_map': answer_likes_map,
        }
        context.update(get_centrifugo_data(request))

        return render(request, 'questions/question.html', context)

class AskQuestionView(LoginRequiredMixin, CreateView):
    """Форма создания вопроса"""
    template_name = 'questions/ask.html'
    form_class = QuestionForm

    def form_valid(self, form):
        new_question = form.save(author=self.request.user)
        return redirect('question', question_id=new_question.id)


class QuestionLikeAjaxView(LoginRequiredApiMixin, View):
    """AJAX обработчик лайков/дизлайков для вопросов"""
    def post(self, request, question_id, *args, **kwargs):
        vote_type = request.POST.get('type')

        if vote_type not in ['like', 'dislike']:
            return JsonResponse({'error': 'Неверный тип оценки.'}, status=400)

        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            return JsonResponse({'error': 'Вопрос не найден.'}, status=404)

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

        question.sync_rating()

        if like_obj.is_active:
            current_vote = 'like' if like_obj.is_like else 'dislike'
        else:
            current_vote = 'none'

        return JsonResponse({'rating': question.rating, 'vote': current_vote})


class AnswerLikeAjaxView(LoginRequiredApiMixin, View):
    """AJAX обработчик лайков/дизлайков для ответов"""
    def post(self, request, answer_id, *args, **kwargs):
        vote_type = request.POST.get('type')

        if vote_type not in ['like', 'dislike']:
            return JsonResponse({'error': 'Неверный тип оценки.'}, status=400)

        try:
            answer = Answer.objects.get(pk=answer_id)
        except Answer.DoesNotExist:
            return JsonResponse({'error': 'Ответ не найден.'}, status=404)

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

        answer.sync_rating()

        if like_obj.is_active:
            current_vote = 'like' if like_obj.is_like else 'dislike'
        else:
            current_vote = 'none'

        return JsonResponse({'rating': answer.rating, 'vote': current_vote})


class MarkCorrectAnswerAjaxView(LoginRequiredApiMixin, View):
    """AJAX обработчик отметки правильного ответа"""
    def post(self, request, question_id, answer_id, *args, **kwargs):
        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            return JsonResponse({'error': 'Вопрос не найден.'}, status=404)

        try:
            answer = Answer.objects.get(pk=answer_id)
        except Answer.DoesNotExist:
            return JsonResponse({'error': 'Ответ не найден.'}, status=404)

        if question.author != request.user:
            return JsonResponse({'error': 'Только автор вопроса может отмечать правильный ответ.'}, status=403)

        if answer.question != question:
            return JsonResponse({'error': 'Этот ответ не относится к данному вопросу.'}, status=400)

        status_correct = answer.toggle_correct()

        return JsonResponse({'is_correct': status_correct, 'answer_id': answer.id})


class SearchQuestionsAjaxView(View):
    """API для полнотекстового поиска (выпадающая подсказка)"""
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()

        if len(query) < 2:
            return JsonResponse({'results': []})

        search_vector = SearchVector('title', weight='A', config='english') + SearchVector('text', weight='B', config='english')
        search_query = SearchQuery(query, config='english')

        questions_qs = Question.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(search=search_query).order_by('-rank', '-id').values('id', 'title')[:5]

        results = list(questions_qs)

        return JsonResponse({'results': results})
