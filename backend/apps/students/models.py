from django.db import models
from django.conf import settings


class StudentClass(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=100)  # e.g. "Class 10A"
    board = models.CharField(max_length=10, default='RBSE')
    section = models.CharField(max_length=10, blank=True)
    academic_year = models.CharField(max_length=10, default='2024-25')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.teacher.get_full_name()}"

    class Meta:
        ordering = ['name']


class Student(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='students')
    student_class = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.roll_number})"

    class Meta:
        ordering = ['last_name', 'first_name']
