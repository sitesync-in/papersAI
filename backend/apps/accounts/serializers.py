from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'password', 'role', 'school_name', 'district', 'preferred_language']
        extra_kwargs = {'email': {'required': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid credentials.')
        user = authenticate(username=user.username, password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials.')
        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role',
                  'school_name', 'district', 'employee_id', 'shala_darpan_id',
                  'udise_code', 'phone', 'preferred_language', 'avatar',
                  'date_joined', 'created_at']
        read_only_fields = ['id', 'username', 'date_joined', 'created_at']


class SSOSerializer(serializers.Serializer):
    sso_token = serializers.CharField()
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='teacher')
