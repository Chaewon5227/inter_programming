from django.contrib import admin
from .models import Account, Category, Transaction, BudgetPeriod, BudgetItem

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("id","owner","name","type","balance")
    list_filter = ("type",)
    search_fields = ("name",)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id","owner","name","kind")
    list_filter = ("kind",)
    search_fields = ("name",)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id","owner","account","category","amount","occurred_at","created_at")
    list_filter = ("category__kind","account")
    search_fields = ("memo",)

@admin.register(BudgetPeriod)
class BudgetPeriodAdmin(admin.ModelAdmin):
    list_display = ("id","owner","start_date","end_date")
    ordering = ("-start_date",)

@admin.register(BudgetItem)
class BudgetItemAdmin(admin.ModelAdmin):
    list_display = ("id","period","category","limit_amount")
