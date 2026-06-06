from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from courses.models import Course, Review
from users.models import Profile, EmailVerification
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

        # 6 xonali kod yaratish
        code = EmailVerification.generate_code()

        # Oldingi kodlarni o'chirish
        EmailVerification.objects.filter(email=email).delete()

        # Yangi kod saqlash
        EmailVerification.objects.create(
            email=email,
            code=code
        )

        # Session ga ma'lumotlarni saqlash
        request.session['register_username'] = username
        request.session['register_email'] = email
        request.session['register_password'] = password1

        # Email yuborish
        send_mail(
            subject='LearnUz — Email tasdiqlash kodi',
            message=f'Salom {username}!\n\nLearnUz ga ro\'yxatdan o\'tish uchun tasdiqlash kodingiz:\n\n🔐 {code}\n\nKod 10 daqiqa davomida amal qiladi.\n\nAgar siz ro\'yxatdan o\'tmagan bo\'lsangiz, bu xabarni e\'tiborsiz qoldiring.',
            from_email='aslonovdiyorbek333@gmail.com',
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, f'✅ {email} manziliga 6 xonali kod yuborildi! Emailingizni tekshiring.')
        return redirect('verify_email')

    return render(request, 'users/register.html')


def verify_email(request):
    email = request.session.get('register_email')
    username = request.session.get('register_username')

    if not email:
        return redirect('register')

    if request.method == 'POST':
        code = request.POST.get('code')

        try:
            verification = EmailVerification.objects.get(email=email, code=code, is_verified=False)
            verification.is_verified = True
            verification.save()

            # Foydalanuvchi yaratish
            password = request.session.get('register_password')
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=True
            )

            # Sessionni tozalash
            del request.session['register_username']
            del request.session['register_email']
            del request.session['register_password']

            login(request, user)
            messages.success(request, f'🎉 Xush kelibsiz, {username}! Email muvaffaqiyatli tasdiqlandi!')
            return redirect('home')

        except EmailVerification.DoesNotExist:
            messages.error(request, '❌ Kod xato! Qaytadan tekshiring.')

    return render(request, 'users/verify_email.html', {'email': email})


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


@login_required
def profile(request):
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