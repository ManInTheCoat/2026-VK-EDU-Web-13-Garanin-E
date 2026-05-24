from django.urls import path
from questions import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('hot/', views.HotQuestionsView.as_view(), name='hot'),
    path('ask/', views.AskQuestionView.as_view(), name='ask'),
    path('tag/<str:tag_name>/', views.TagQuestionsView.as_view(), name='tag'),
    path('question/<int:question_id>/', views.QuestionDetailView.as_view(), name='question'),
    path('ajax/like-question/', views.QuestionLikeAjaxView.as_view(), name='like_question'),
    path('ajax/like-answer/', views.AnswerLikeAjaxView.as_view(), name='like_answer'),
    path('ajax/mark-correct/', views.MarkCorrectAnswerAjaxView.as_view(), name='mark_correct'),
]
