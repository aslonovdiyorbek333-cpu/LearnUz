from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
import re


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validatsiya
        errors = []

        if len(username) < 3:
            errors.append('Username kamida 3 ta harf bo\'lishi kerak!')

        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username faqat harf, raqam va _ dan iborat bo\'lishi kerak!')

        if User.objects.filter(username=username).exists():
            errors.append('Bu username allaqachon mavjud!')

        if email and User.objects.filter(email=email).exists():
            errors.append('Bu email allaqachon ro\'yxatdan o\'tgan!')

        if len(password1) < 8:
            errors.append('Parol kamida 8 ta belgi bo\'lishi kerak!')

        if not re.search(r'[A-Z]', password1):
            errors.append('Parolda kamida 1 ta katta harf bo\'lishi kerak!')

        if not re.search(r'[0-9]', password1):
            errors.append('Parolda kamida 1 ta raqam bo\'lishi kerak!')

        if password1 != password2:
            errors.append('Parollar mos kelmadi!')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'users/register.html', {
                'username': username,
                'email': email,
            })

        # Foydalanuvchi yaratish
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        login(request, user)
        messages.success(request, 'Muvaffaqiyatli ro\'yxatdan o\'tdingiz!')
        return redirect('home')

    return render(request, 'users/register.html')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Muvaffaqiyatli kirdingiz!')
            return redirect('home')
        else:
            messages.error(request, 'Username yoki parol xato!')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Muvaffaqiyatli chiqdingiz!')
    return redirect('home')


def profile(request):
    return render(request, 'users/profile.html')