from django.contrib import admin
from .models import Paper

@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ['title', 'board', 'class_name', 'subject', 'difficulty', 'status', 'teacher', 'created_at']
    list_filter = ['board', 'status', 'difficulty']
    search_fields = ['title', 'subject', 'teacher__email']
