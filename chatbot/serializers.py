# chatbot/serializers.py
from rest_framework import serializers
from .models import Submission, Agency, Appointment
from django.contrib.auth.models import User


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
        )
        return user


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "service_type",
            "identity_document",
            "selfie",
            "status",
            "rejection_reason",
            "created_at",
        ]
        read_only_fields = ["status", "rejection_reason", "created_at"]


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ["id", "name", "latitude", "longitude", "address"]


class AppointmentSerializer(serializers.ModelSerializer):
    agency = AgencySerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "full_name",
            "email",
            "agency",
            "submission",
            "time",
            "qr_code",
            "created_at",
        ]
        read_only_fields = ["time", "qr_code", "created_at"]
