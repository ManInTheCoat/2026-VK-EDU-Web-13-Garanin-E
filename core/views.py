from django.shortcuts import render

def login(request):
  """Страница авторизации"""
  return render(request, 'core/login.html')

def signup(request):
  """Страница регистрации"""
  return render(request, 'core/signup.html')

def profile(request):
  """Страница редактирования профиля"""
  return render(request, 'core/profile.html')
