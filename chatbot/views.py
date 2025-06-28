from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
import os
from django.conf import settings
from .bcbai import (
    send_message,
    get_chat,
    load_json_dataset,
)
from .models import Submission
from .serializers import SignupSerializer, SubmissionSerializer
import numpy as np
from rest_framework.permissions import AllowAny
from .models import Agency, Appointment
from .serializers import AgencySerializer, AppointmentSerializer
from datetime import datetime, timedelta
import uuid
import qrcode
from django.core.files.base import ContentFile
from io import BytesIO

# from deepface import DeepFace


class ChatMessageView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Extract question from request data
        question = request.data.get("question")
        if not question:
            return Response(
                {"error": "Question is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create a unique session_key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        # Call send_message directly; it now handles intent detection and response generation
        try:
            answer = send_message(question, session_key)
            return Response({"reply": answer})
        except Exception as e:
            return Response(
                {"error": f"Error processing question: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ServiceListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            dataset = load_json_dataset()
            # To list services, you'll need to iterate through the intents
            # and extract the service names from the 'responses' section of 'informations_service' intent.
            service_info_intent = next(
                (
                    intent
                    for intent in dataset.get("intents", [])
                    if intent["intent_name"] == "informations_service"
                ),
                None,
            )

            if service_info_intent:
                services_list = []
                for service_key, service_details in service_info_intent[
                    "responses"
                ].items():
                    # For simplicity, returning just the French name and description
                    services_list.append(
                        {
                            "name_fr": service_key,  # Service key itself is the FR name for now
                            "description_fr": service_details.get(
                                "fr", "No description available."
                            ),
                        }
                    )
                return Response(services_list, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Service information intent not found in dataset."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except Exception as e:
            return Response(
                {"error": f"Error retrieving services: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SubmissionAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            submission = serializer.save()

            is_valid, message = verify_identity(
                submission.selfie.path, submission.identity_document.path
            )
            if is_valid:
                submission.status = "verified"
                submission.save()
                return Response(
                    {
                        "message": "Documents soumis et vérifiés avec succès",
                        "submission_id": submission.id,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                submission.status = "rejected"
                submission.rejection_reason = message
                submission.save()
                return Response(
                    {"message": "Échec de la vérification", "reason": message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def verify_identity(selfie_path, document_path):
    print(f"Vérification des documents : {selfie_path}, {document_path}")
    # try:
    #     result = DeepFace.verify(
    #         img1_path=selfie_path, img2_path=document_path, enforce_detection=True
    #     )
    #     if result["verified"]:
    #         return True, "Vérification réussie"
    #     else:
    #         return False, "Les visages ne correspondent pas"
    # except Exception as e:
    #     return False, f"Erreur lors de la vérification : {str(e)}"


class AgencyListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        agencies = Agency.objects.all()
        serializer = AgencySerializer(agencies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AppointmentAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        agency_id = request.data.get("agency_id")
        submission_id = request.data.get("submission_id")
        try:
            agency = Agency.objects.get(id=agency_id)
            submission = Submission.objects.get(id=submission_id)

            last_appointment = (
                Appointment.objects.filter(agency=agency).order_by("-time").first()
            )
            if last_appointment:
                new_time = last_appointment.time + timedelta(minutes=15)
            else:
                new_time = datetime.now().replace(
                    hour=9, minute=0, second=0, microsecond=0
                )
            # Générer un QR code
            qr_data = f"appointment:{submission.id}:{uuid.uuid4()}"
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#0d6efd", back_color="#f8f9fa")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qr_file = ContentFile(buffer.getvalue(), name=f"qr_{qr_data}.png")
            # Créer le rendez-vous
            appointment = Appointment.objects.create(
                agency=agency,
                submission=submission,
                time=new_time,
                qr_code=qr_data,
            )
            # Sauvegarder le QR code (optionnel, pour stockage)
            appointment.qr_code_file = qr_file
            appointment.save()
            serializer = AppointmentSerializer(appointment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Agency.DoesNotExist:
            return Response(
                {"message": "Agence non trouvée"}, status=status.HTTP_404_NOT_FOUND
            )
        except Submission.DoesNotExist:
            return Response(
                {"message": "Soumission non trouvée ou non autorisée"},
                status=status.HTTP_404_NOT_FOUND,
            )


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "Compte créé avec succès"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
