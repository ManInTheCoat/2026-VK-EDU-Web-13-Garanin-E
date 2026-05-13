from django.urls import path
from questions import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('hot/', views.HotQuestionsView.as_view(), name='hot'),
    path('ask/', views.AskQuestionView.as_view(), name='ask'),
    path('tag/<str:tag_name>/', views.TagQuestionsView.as_view(), name='tag'),
    path('question/<int:question_id>/', views.QuestionDetailView.as_view(), name='question'),
]
