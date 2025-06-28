from django.urls import path
from . import views

app_name = "chatbot"

urlpatterns = [
    path("api/message/", views.ChatMessageView.as_view(), name="chat_message"),
    path("api/services/", views.ServiceListView.as_view(), name="service_list"),
    path("submit/", views.SubmissionAPIView.as_view(), name="submit_documents"),
    path("agencies/", views.AgencyListAPIView.as_view(), name="agency_list"),
    path(
        "appointments/", views.AppointmentAPIView.as_view(), name="create_appointment"
    ),
    path("signup/", views.SignupView.as_view(), name="signup"),
]
