from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .models import Course, Category, Lesson, Review
from users.models import Enrollment


def home(request):
    courses = Course.objects.filter(is_published=True)[:6]
    categories = Category.objects.all()
    context = {
        'courses': courses,
        'categories': categories,
    }
    return render(request, 'courses/home.html', context)


def course_list(request):
    courses = Course.objects.filter(is_published=True)
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    query = request.GET.get('q')
    if category_id:
        courses = courses.filter(category_id=category_id)
    if query:
        courses = courses.filter(title__icontains=query) | courses.filter(description__icontains=query)
    context = {
        'courses': courses,
        'categories': categories,
        'query': query,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    lessons = course.lesson_set.all()
    reviews = course.reviews.all()
    is_enrolled = False
    user_review = None
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            user=request.user, course=course
        ).exists()
        user_review = Review.objects.filter(
            user=request.user, course=course
        ).first()

    if request.method == 'POST' and request.user.is_authenticated:
        if not user_review:
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')
            if rating and comment:
                Review.objects.create(
                    user=request.user,
                    course=course,
                    rating=int(rating),
                    comment=comment
                )
                messages.success(request, 'Sharhingiz qo\'shildi!')
                return redirect('course_detail', pk=pk)

    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']

    context = {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'reviews': reviews,
        'user_review': user_review,
        'avg_rating': avg_rating,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, 'Siz bu kursga allaqachon yozilgansiz!')
        return redirect('course_detail', pk=pk)
    Enrollment.objects.create(user=request.user, course=course)
    messages.success(request, f'Siz "{course.title}" kursiga muvaffaqiyatli yozildingiz!')
    return redirect('course_detail', pk=pk)


@login_required
def lesson_detail(request, course_pk, lesson_pk):
    course = get_object_or_404(Course, pk=course_pk)
    lesson = get_object_or_404(Lesson, pk=lesson_pk, course=course)
    is_enrolled = Enrollment.objects.filter(
        user=request.user, course=course
    ).exists()
    if not is_enrolled and not request.user.is_staff:
        messages.warning(request, 'Bu darsni ko\'rish uchun kursga yoziling!')
        return redirect('course_detail', pk=course_pk)
    lessons = course.lesson_set.all()
    context = {
        'course': course,
        'lesson': lesson,
        'lessons': lessons,
    }
    return render(request, 'courses/lesson_detail.html', context)