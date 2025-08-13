# accounts/views.py
from drf_spectacular.utils import (
    extend_schema, OpenApiResponse, OpenApiExample, OpenApiParameter
)
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken

def tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh["role"] = user.role
    return {"access": str(refresh.access_token), "refresh": str(refresh)}

X_REQUEST_ID = OpenApiParameter(
    name="X-Request-ID",
    type=str,
    location=OpenApiParameter.HEADER,
    required=False,
    description="Optional idempotency/trace header echoed as 'X-Request-ID' in responses.",
)

@extend_schema(
    tags=["Auth"],
    auth=[],  # public
    parameters=[X_REQUEST_ID],
    request=RegisterSerializer,
    responses={
        201: OpenApiResponse(description="User created + tokens"),
        400: OpenApiResponse(description="Validation error"),
        429: OpenApiResponse(description="Rate limited"),
    },
    examples=[
        OpenApiExample(
            "Register payload",
            value={"username": "ali", "email": "ali@example.com", "password": "VeryStrong!Pass1"},
            request_only=True,
        ),
    ],
)
class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "auth"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request):
        s = RegisterSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        data = {
            "user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role},
            "tokens": tokens_for_user(user),
        }
        return Response({"success": True, "data": data, "error": None, "trace_id": request.request_id},
                        status=status.HTTP_201_CREATED)

@extend_schema(
    tags=["Auth"],
    auth=[],  # public
    parameters=[X_REQUEST_ID],
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(description="Logged in + tokens"),
        400: OpenApiResponse(description="Invalid credentials"),
        429: OpenApiResponse(description="Rate limited"),
    },
    examples=[
        OpenApiExample(
            "Login payload (email)",
            value={"username_or_email": "ali@example.com", "password": "VeryStrong!Pass1"},
            request_only=True,
        ),
    ],
)
class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "auth"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.validated_data["user"]
        data = {
            "user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role},
            "tokens": tokens_for_user(user),
        }
        return Response({"success": True, "data": data, "error": None, "trace_id": request.request_id},
                        status=status.HTTP_200_OK)
