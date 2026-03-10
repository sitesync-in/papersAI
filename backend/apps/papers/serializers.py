from rest_framework import serializers
from .models import Paper


class PaperListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = ['id', 'title', 'board', 'class_name', 'subject',
                  'difficulty', 'status', 'credits_used', 'created_at']


class PaperDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = '__all__'
        read_only_fields = ['teacher', 'status', 'paper_content', 'answer_key',
                            'paper_text', 'answer_key_text', 'pdf_file', 'created_at', 'updated_at']


class PaperGenerateSerializer(serializers.Serializer):
    board = serializers.ChoiceField(choices=['RBSE', 'RTU', 'CBSE'])
    class_name = serializers.CharField(max_length=30)
    subject = serializers.CharField(max_length=100)
    difficulty = serializers.ChoiceField(choices=['easy', 'balanced', 'hard'], default='balanced')
    topics = serializers.CharField(required=False, allow_blank=True, default='')
    adhere_marking_scheme = serializers.BooleanField(default=True)
    preferred_language = serializers.ChoiceField(choices=['en', 'hi'], required=False)
    branch = serializers.CharField(required=False, allow_blank=True, max_length=50, help_text='RTU Branch (e.g., CSE)')
    semester = serializers.CharField(required=False, allow_blank=True, max_length=20, help_text='RTU Semester')
