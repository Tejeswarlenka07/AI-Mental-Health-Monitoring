from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import UserProfile


def home(request):
    return render(request, 'home.html')


def register_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():

            return render(
                request,
                'users/register.html',
                {
                    'error': 'Username already exists'
                }
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect('dashboard')

    return render(request, 'users/register.html')


def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('dashboard')

        return render(
            request,
            'users/login.html',
            {
                'error': 'Invalid username or password'
            }
        )

    return render(request, 'users/login.html')


def logout_view(request):

    logout(request)

    return redirect('home')


@login_required
def profile_view(request):

    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':

        age = request.POST.get('age')
        bio = request.POST.get('bio')

        profile.age = age
        profile.bio = bio

        profile.save()

        return redirect('profile')

    return render(
        request,
        'users/profile.html',
        {
            'profile': profile
        }
    )