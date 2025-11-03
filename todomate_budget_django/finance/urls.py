from django.urls import path
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Transaction, Account, Category
from django.db.models import Sum

def transaction_list(request):
    if not request.user.is_authenticated:
        return redirect('/admin/login/?next=' + request.path)
    txs = Transaction.objects.filter(owner=request.user).select_related('account','category')
    totals = txs.values('category__kind').annotate(total=Sum('amount'))
    return render(request, 'finance/list.html', {'transactions': txs, 'totals': totals})

def transaction_create(request):
    if not request.user.is_authenticated:
        return redirect('/admin/login/?next=' + request.path)
    if request.method == 'POST':
        account_id = request.POST.get('account')
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        memo = request.POST.get('memo','')
        occurred_at = request.POST.get('occurred_at')
        Transaction.objects.create(
            owner=request.user,
            account_id=account_id,
            category_id=category_id,
            amount=amount,
            memo=memo,
            occurred_at=occurred_at
        )
        return redirect('/finance/')
    accounts = Account.objects.filter(owner=request.user)
    categories = Category.objects.filter(owner=request.user)
    return render(request, 'finance/create.html', {'accounts': accounts, 'categories': categories})

urlpatterns = [
    path('', transaction_list, name='transaction_list'),
    path('new/', transaction_create, name='transaction_create'),
]
