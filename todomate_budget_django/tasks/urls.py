from django.urls import path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Task, Tag

def task_list(request):
    if not request.user.is_authenticated:
        return redirect('/admin/login/?next=' + request.path)
    tasks = Task.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'tasks/list.html', {'tasks': tasks})

def task_create(request):
    if not request.user.is_authenticated:
        return redirect('/admin/login/?next=' + request.path)
    if request.method == 'POST':
        title = request.POST.get('title')
        due_at = request.POST.get('due_at') or None
        Task.objects.create(owner=request.user, title=title, due_at=due_at)
        return redirect('/tasks/')
    return render(request, 'tasks/create.html')

urlpatterns = [
    path('', task_list, name='task_list'),
    path('new/', task_create, name='task_create'),
]
