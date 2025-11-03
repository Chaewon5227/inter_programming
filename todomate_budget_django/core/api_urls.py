from rest_framework.routers import DefaultRouter
from django.urls import path, include
from tasks.api import TaskViewSet, TagViewSet
from finance.api import AccountViewSet, CategoryViewSet, TransactionViewSet, BudgetPeriodViewSet, BudgetItemViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'tags', TagViewSet, basename='tag')

router.register(r'finance/accounts', AccountViewSet, basename='account')
router.register(r'finance/categories', CategoryViewSet, basename='category')
router.register(r'finance/transactions', TransactionViewSet, basename='transaction')
router.register(r'finance/budget-periods', BudgetPeriodViewSet, basename='budgetperiod')
router.register(r'finance/budget-items', BudgetItemViewSet, basename='budgetitem')

urlpatterns = [
    path('', include(router.urls)),
]
