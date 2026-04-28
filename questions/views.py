from django.shortcuts import render
from .utils import paginate

QUESTIONS = []
for i in range(1, 30):
  QUESTIONS.append({
    'id': i,
    'title': f'Вопрос номер {i}',
    'text': f'Это текст интересного вопроса {i}.',
    'tags': ['python', 'django'] if i % 2 == 0 else ['html', 'css'],
  })

def index(request):
  """Список новых вопросов (главная страница)"""
  page = paginate(QUESTIONS, request, per_page=5)
  return render(request, 'questions/index.html', {'questions': page})

def hot(request):
  """Список лучших вопросов"""
  hot_questions = QUESTIONS[::-1]
  page = paginate(hot_questions, request, per_page=5)
  return render(request, 'questions/index.html', {'questions': page})

def tag(request, tag_name):
  """Список вопросов по тегу"""
  tag_questions = [q for q in QUESTIONS if tag_name in q['tags']]
  page = paginate(tag_questions, request, per_page=5)
  return render(request, 'questions/index.html', {
    'questions': page,
    'tag_name': tag_name
  })

def question(request, question_id):
  """Страница одного вопроса со списком ответов"""
  one_question = next((q for q in QUESTIONS if q['id'] == int(question_id)), None)
  answers = [{'id': i, 'text': f'Это ответ {i}'} for i in range(1, 4)]
  page = paginate(answers, request, per_page=3)
  return render(request, 'questions/question.html', {
    'question': one_question,
    'answers': page,
  })

def ask(request):
  """Форма создания вопроса"""
  return render(request, 'questions/ask.html')
