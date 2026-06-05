from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from courses.models import Course, Review
import re


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        errors = []

        if len(username) < 3:
            errors.append('Username kamida 3 ta harf bo\'lishi kerak!')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username faqat harf, raqam va _ dan iborat bo\'lishi kerak!')
        if User.objects.filter(username=username).exists():
            errors.append('Bu username allaqachon mavjud!')
        if not email:
            errors.append('Email majburiy!')
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

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            is_active=False
        )

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = f"http://127.0.0.1:8000/activate/{uid}/{token}/"

        send_mail(
            subject='LearnUz — Email tasdiqlash',
            message=f'Salom {username}!\n\nEmailingizni tasdiqlash uchun quyidagi havolani bosing:\n\n{activation_link}\n\nHavola 24 soat davomida amal qiladi.',
            from_email='aslonovdiyorbek333@gmail.com',
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, f'{email} manziliga tasdiqlash xati yuborildi! Emailingizni tekshiring.')
        return redirect('login')

    return render(request, 'users/register.html')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Email tasdiqlandi! Xush kelibsiz!')
        return redirect('home')
    else:
        messages.error(request, 'Havola yaroqsiz yoki muddati o\'tgan!')
        return redirect('register')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, 'Emailingizni tasdiqlamadingiz! Pochta qutingizni tekshiring.')
                return render(request, 'users/login.html', {'form': form})
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


@login_required
def profile(request):
    from users.models import Profile
    # Profile yo'q bo'lsa avtomatik yaratish
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    enrollments = request.user.enrollment_set.all()
    total_courses = enrollments.count()
    completed_courses = enrollments.filter(is_completed=True).count()
    reviews = Review.objects.filter(user=request.user)

    if request.method == 'POST':
        bio = request.POST.get('bio', '')
        phone = request.POST.get('phone', '')
        avatar = request.FILES.get('avatar')
        profile.bio = bio
        profile.phone = phone
        if avatar:
            profile.avatar = avatar
        profile.save()
        messages.success(request, 'Profil muvaffaqiyatli yangilandi!')
        return redirect('profile')

    context = {
        'profile': profile,
        'enrollments': enrollments,
        'total_courses': total_courses,
        'completed_courses': completed_courses,
        'reviews': reviews,
    }
    return render(request, 'users/profile.html', context)