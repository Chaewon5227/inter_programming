from rest_framework import serializers
from tasks.models import Task
from .models import Account, Category, Transaction, BudgetPeriod, BudgetItem

class AccountSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    class Meta:
        model = Account
        fields = ["id","owner","name","type","balance"]

class CategorySerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    class Meta:
        model = Category
        fields = ["id","owner","name","kind"]

class TransactionSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    # 일정 연동을 위해 Task 기본 키를 직접 주고받는다.
    task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Transaction
        fields = ["id","owner","account","category","task","amount","memo","occurred_at","created_at"]

class BudgetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetItem
        fields = ["id","period","category","limit_amount"]

class BudgetPeriodSerializer(serializers.ModelSerializer):
    items = BudgetItemSerializer(many=True, read_only=True)
    class Meta:
        model = BudgetPeriod
        fields = ["id","owner","start_date","end_date","items"]
