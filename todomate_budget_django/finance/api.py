from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Account, Category, Transaction, BudgetPeriod, BudgetItem
from .serializers import AccountSerializer, CategorySerializer, TransactionSerializer, BudgetPeriodSerializer, BudgetItemSerializer

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, "owner_id", None) == request.user.id

class OwnerViewSetMixin:
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class AccountViewSet(OwnerViewSetMixin, viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    filterset_fields = ["type","name"]
    search_fields = ["name"]
    ordering_fields = ["name","balance","id"]

class CategoryViewSet(OwnerViewSetMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ["kind","name"]
    search_fields = ["name"]
    ordering_fields = ["name","id"]

class TransactionViewSet(OwnerViewSetMixin, viewsets.ModelViewSet):
    queryset = Transaction.objects.select_related("account","category","task")
    serializer_class = TransactionSerializer
    filterset_fields = ["category__kind","account","category","occurred_at","task"]
    search_fields = ["memo"]
    ordering_fields = ["occurred_at","amount","id"]

class BudgetPeriodViewSet(OwnerViewSetMixin, viewsets.ModelViewSet):
    queryset = BudgetPeriod.objects.all().prefetch_related("items")
    serializer_class = BudgetPeriodSerializer
    filterset_fields = ["start_date","end_date"]
    ordering_fields = ["start_date","end_date","id"]

class BudgetItemViewSet(viewsets.ModelViewSet):
    queryset = BudgetItem.objects.select_related("period","category")
    serializer_class = BudgetItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["period","category"]
    ordering_fields = ["id"]
