from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_TEACHER = 'teacher'
    ROLE_STUDENT = 'student'
    ROLE_CHOICES = [(ROLE_TEACHER, 'Teacher'), (ROLE_STUDENT, 'Student')]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_TEACHER)
    school_name = models.CharField(max_length=200, blank=True)
    district = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=50, blank=True)
    shala_darpan_id = models.CharField(max_length=50, blank=True)
    udise_code = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    preferred_language = models.CharField(max_length=10, choices=[('en', 'English'), ('hi', 'Hindi')], default='en')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
