from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer, SSOSerializer
from .models import User
import uuid


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': UserProfileSerializer(user).data,
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        summary='Register a new educator account',
        tags=['Authentication'],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Auto-create credit wallet
            from apps.subscriptions.models import CreditWallet
            CreditWallet.objects.create(user=user, credits=50)  # 50 free credits
            tokens = get_tokens_for_user(user)
            return Response(tokens, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        summary='Login with email and password',
        tags=['Authentication'],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = get_tokens_for_user(user)
            return Response(tokens)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SSOLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=SSOSerializer,
        summary='Login via SSO Rajasthan (stub)',
        tags=['Authentication'],
    )
    def post(self, request):
        serializer = SSOSerializer(data=request.data)
        if serializer.is_valid():
            # SSO stub — in production this would verify with Rajasthan SSO provider
            sso_token = serializer.validated_data['sso_token']
            role = serializer.validated_data['role']
            # Find or create user based on SSO token (using token as username stub)
            username = f"sso_{sso_token[:16]}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f"{username}@sso.rajasthan.gov.in",
                    'first_name': 'SSO',
                    'last_name': 'User',
                    'role': role,
                }
            )
            if created:
                user.set_unusable_password()
                user.save()
                from apps.subscriptions.models import CreditWallet
                CreditWallet.objects.create(user=user, credits=50)
            return Response(get_tokens_for_user(user))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Get current user profile', tags=['Authentication'])
    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Get or update user profile', tags=['Authentication'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary='Refresh JWT token', tags=['Authentication'])
    def post(self, request):
        try:
            refresh = RefreshToken(request.data.get('refresh'))
            return Response({'access': str(refresh.access_token)})
        except Exception:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)
