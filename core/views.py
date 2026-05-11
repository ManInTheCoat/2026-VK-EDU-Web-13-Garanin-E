from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import reverse
from .forms import LoginForm, SignupForm, ProfileForm

def login_view(request):
    """Страница авторизации"""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)

                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url and url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)

                return redirect('index')
            else:
                form.add_error(None, "Sorry, wrong login or password. Please try again.")
    else:
        form = LoginForm()

    return render(request, 'core/login.html', {'form': form})

def signup_view(request):
    """Страница регистрации"""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignupForm()

    return render(request, 'core/signup.html', {'form': form})

@login_required(login_url='login')
def profile_view(request):
    """Страница редактирования профиля"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'core/profile.html', {'form': form})

def logout_view(request):
    """Выход пользователя"""
    logout(request)

    next_url = request.META.get('HTTP_REFERER', reverse('index'))

    if url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect('index')
