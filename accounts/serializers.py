from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, JobSeekerProfile, CompanyProfile


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "username", "password", "password_confirm","role", "phone_number",)
        

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        if attrs.get("role") not in (User.Role.JOBSEEKER, User.Role.COMPANY):
            raise serializers.ValidationError({"role": "role must be 'jobseeker' or 'company'."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "username": self.user.username,
            "role": self.user.role,
        }
        return data


class JobSeekerProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    skills_list = serializers.ListField(read_only=True)

    class Meta:
        model = JobSeekerProfile
        fields = ("id", "email", "first_name", "last_name", "birth_date", "address","bio",
                  "education", "skills", "skills_list", "experience_years","resume_file",
                  "created_at", "updated_at",)
            
        read_only_fields = ("id", "created_at", "updated_at")


class CompanyProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = CompanyProfile
        fields = ("id", "email", "company_name", "description", "website",
                  "address","industry", "logo", "founded_year", "created_at", "updated_at",)
            
        read_only_fields = ("id", "created_at", "updated_at")


class CompanyPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ("id", "company_name", "description", "website", "industry", "logo")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "username", "role", "phone_number", "is_verified", "date_joined")
        read_only_fields = fields


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
