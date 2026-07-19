from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from core.permissions import IsJobSeeker, IsCompany

from .models import User, JobSeekerProfile, CompanyProfile
from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    JobSeekerProfileSerializer,
    CompanyProfileSerializer,
    UserSerializer,
    ChangePasswordSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "Registration successful.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"old_password": "Incorrect password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"message": "Password updated successfully."})


class JobSeekerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = JobSeekerProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobSeeker]

    def get_object(self):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=self.request.user)
        return profile


class CompanyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CompanyProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompany]

    def get_object(self):
        profile, _ = CompanyProfile.objects.get_or_create(
            user=self.request.user,
            defaults={"company_name": self.request.user.username},
        )
        return profile


class CompanyPublicDetailView(generics.RetrieveAPIView):
    queryset = CompanyProfile.objects.all()
    serializer_class = CompanyProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"
