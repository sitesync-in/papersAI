from django.db import models
from django.conf import settings


class Paper(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_GENERATING = 'generating'
    STATUS_READY = 'ready'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_GENERATING, 'Generating'),
        (STATUS_READY, 'Ready'),
        (STATUS_FAILED, 'Failed'),
    ]

    BOARD_RBSE = 'RBSE'
    BOARD_RTU = 'RTU'
    BOARD_CBSE = 'CBSE'
    BOARD_CHOICES = [(BOARD_RBSE, 'RBSE'), (BOARD_RTU, 'RTU'), (BOARD_CBSE, 'CBSE')]

    DIFFICULTY_EASY = 'easy'
    DIFFICULTY_BALANCED = 'balanced'
    DIFFICULTY_HARD = 'hard'
    DIFFICULTY_CHOICES = [(DIFFICULTY_EASY, 'Easy'), (DIFFICULTY_BALANCED, 'Balanced'), (DIFFICULTY_HARD, 'Hard')]

    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='papers')
    title = models.CharField(max_length=300, blank=True)
    board = models.CharField(max_length=10, choices=BOARD_CHOICES, default=BOARD_RBSE)
    class_name = models.CharField(max_length=30)
    subject = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default=DIFFICULTY_BALANCED)
    topics = models.TextField(blank=True, help_text='Comma separated custom topics')
    adhere_marking_scheme = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    # RTU-specific fields
    branch = models.CharField(max_length=50, blank=True, null=True, help_text='RTU Branch (e.g., CSE, ECE)')
    semester = models.CharField(max_length=20, blank=True, null=True, help_text='RTU Semester (e.g., 1, 2, 3)')

    # Generated content
    paper_content = models.JSONField(null=True, blank=True)
    answer_key = models.JSONField(null=True, blank=True)
    paper_text = models.TextField(blank=True)
    answer_key_text = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='papers/', null=True, blank=True)

    credits_used = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.board} | {self.class_name} | {self.subject} — {self.teacher.get_full_name()}"
