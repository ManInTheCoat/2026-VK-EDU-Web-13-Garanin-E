from django.urls import path
from questions import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('hot/', views.HotQuestionsView.as_view(), name='hot'),
    path('ask/', views.AskQuestionView.as_view(), name='ask'),
    path('tag/<str:tag_name>/', views.TagQuestionsView.as_view(), name='tag'),
    path('question/<int:question_id>/', views.QuestionDetailView.as_view(), name='question'),

    path('ajax/question/<int:question_id>/like/', views.QuestionLikeAjaxView.as_view(), name='like_question'),
    path('ajax/answer/<int:answer_id>/like/', views.AnswerLikeAjaxView.as_view(), name='like_answer'),
    path('ajax/question/<int:question_id>/answer/<int:answer_id>/correct/', views.MarkCorrectAnswerAjaxView.as_view(), name='mark_correct'),

    path('answer/<int:answer_id>/html/', views.SingleAnswerHTMLView.as_view(), name='answer_html'),
    path('ajax/search/', views.SearchQuestionsAjaxView.as_view(), name='search_ajax'),
]
