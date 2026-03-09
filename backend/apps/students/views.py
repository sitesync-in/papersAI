from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Student, StudentClass
from .serializers import StudentSerializer, StudentClassSerializer


class StudentClassListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentClassSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='List or create student classes', tags=['Students'])
    def get_queryset(self):
        return StudentClass.objects.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class StudentListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='List or add students', tags=['Students'])
    def get_queryset(self):
        return Student.objects.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Retrieve, update, or delete a student', tags=['Students'])
    def get_queryset(self):
        return Student.objects.filter(teacher=self.request.user)
