from django.contrib import admin
from .models import Student, StudentClass

@admin.register(StudentClass)
class StudentClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'board', 'section', 'teacher', 'academic_year']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'roll_number', 'student_class', 'teacher']
    list_filter = ['student_class']
    search_fields = ['first_name', 'last_name', 'roll_number']
