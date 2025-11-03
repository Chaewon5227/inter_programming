from django.contrib import admin
from .models import Task, Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id","name","color")
    search_fields = ("name",)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id","title","owner","status","priority","start_at","due_at","created_at")
    list_filter = ("status","priority","tags")
    search_fields = ("title","description")
    autocomplete_fields = ("tags",)
