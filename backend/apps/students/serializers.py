from rest_framework import serializers
from .models import Student, StudentClass


class StudentClassSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = StudentClass
        fields = ['id', 'name', 'board', 'section', 'academic_year', 'student_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_student_count(self, obj):
        return obj.students.count()


class StudentSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='student_class.name', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'roll_number', 'email',
                  'phone', 'student_class', 'class_name', 'created_at']
        read_only_fields = ['id', 'created_at']
