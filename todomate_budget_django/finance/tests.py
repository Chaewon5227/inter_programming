from django.test import TestCase
from django.contrib.auth.models import User
from .models import Account, Category, Transaction
from django.utils import timezone
from decimal import Decimal

class FinanceModelsTest(TestCase):
    def setUp(self):
        self.u = User.objects.create_user(username='u1', password='p')
        self.a = Account.objects.create(owner=self.u, name='Wallet', type='cash')
        self.c = Category.objects.create(owner=self.u, name='Food', kind='expense')

    def test_transaction(self):
        tx = Transaction.objects.create(owner=self.u, account=self.a, category=self.c, amount=Decimal("10.50"), occurred_at=timezone.now())
        self.assertEqual(tx.account, self.a)
