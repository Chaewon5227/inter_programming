from django.test import TestCase
from django.contrib.auth.models import User
from .models import Task

class TaskModelTest(TestCase):
    def test_create_task(self):
        u = User.objects.create_user(username='u1', password='p')
        t = Task.objects.create(owner=u, title='Test')
        self.assertEqual(t.owner, u)
        self.assertEqual(t.status, 'todo')
