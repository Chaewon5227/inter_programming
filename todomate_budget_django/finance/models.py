from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Account(models.Model):
    TYPE_CHOICES = [
        ("cash","Cash"),
        ("bank","Bank"),
        ("card","Card"),
        ("other","Other"),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="cash")
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        unique_together = ("owner","name")

    def __str__(self):
        return f"{self.name} ({self.owner})"

class Category(models.Model):
    KIND_CHOICES = [("expense","Expense"), ("income","Income"), ("transfer","Transfer")]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)

    class Meta:
        unique_together = ("owner","name","kind")

    def __str__(self):
        return f"{self.name} [{self.kind}]"

class Transaction(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='transactions')
    # 일정과 소비를 함께 관리할 수 있도록 업무(Task)와의 연결 고리를 둔다.
    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.SET_NULL,
        related_name='linked_transactions',
        null=True,
        blank=True,
        help_text='관련된 일정이 있다면 선택합니다.'
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    memo = models.CharField(max_length=255, blank=True)
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-occurred_at","-created_at"]

    def __str__(self):
        return f"{self.category.kind}: {self.amount} on {self.occurred_at.date()}"

class BudgetPeriod(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budget_periods')
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        unique_together = ("owner","start_date","end_date")
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.start_date} ~ {self.end_date}"

class BudgetItem(models.Model):
    period = models.ForeignKey(BudgetPeriod, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budget_items')
    limit_amount = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        unique_together = ("period","category")

    def __str__(self):
        return f"{self.category.name}: {self.limit_amount}"
