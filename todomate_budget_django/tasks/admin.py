from django.contrib import admin
from .models import Task, Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id","name","owner","color")
    list_filter = ("owner",)
    search_fields = ("name","owner__username")

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id","title","owner","status","priority","start_at","due_at","todo_date","created_at")
    list_filter = ("status","priority","todo_date","tags")
    search_fields = ("title","description")
    autocomplete_fields = ("tags",)
