# accounts/serializers.py
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), lookup="iexact")],
    )

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        # Default role is customer in your custom User model
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        ue = attrs.get("username_or_email")
        password = attrs.get("password")

        # Resolve to username if an email was provided
        user = User.objects.filter(Q(username__iexact=ue) | Q(email__iexact=ue)).first()
        if not user:
            raise serializers.ValidationError({"username_or_email": "User not found."})

        user = authenticate(username=user.username, password=password)
        if not user:
            raise serializers.ValidationError({"password": "Invalid credentials."})

        if not user.is_active:
            raise serializers.ValidationError({"non_field_errors": ["User is inactive."]})

        attrs["user"] = user
        return attrs
