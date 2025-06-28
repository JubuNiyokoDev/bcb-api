from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import JSONField
from django.contrib.auth.models import User


class Submission(models.Model):
    full_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    service_type = models.CharField(
        max_length=100,
        choices=[
            ("sesame", "Carte SESAME"),
            ("visa", "Carte VISA"),
            ("boaweb", "BOAWEB"),
            ("muhira", "Compte Muhira"),
            ("transfer", "Transfert à l’étranger"),
        ],
    )
    identity_document = models.FileField(upload_to="documents/%Y/%m/%d/")
    selfie = models.ImageField(upload_to="selfies/%Y/%m/%d/")
    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "En attente"),
            ("verified", "Vérifié"),
            ("rejected", "Rejeté"),
        ],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.full_name or 'Anonyme'} - {self.service_type} - {self.status}"


class Service(models.Model):
    name = JSONField(
        verbose_name=_("Service Name"),
        help_text=_(
            "Name in multiple languages: {'fr': '...', 'rn': '...', 'en': '...'}"
        ),
    )
    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    description = JSONField(
        verbose_name=_("Description"), help_text=_("Description in multiple languages")
    )
    required_documents = models.JSONField(
        verbose_name=_("Required Documents"), help_text=_("List of required documents")
    )
    eligibility = JSONField(
        verbose_name=_("Eligibility"),
        help_text=_("Eligibility criteria in multiple languages"),
    )

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")

    def __str__(self):
        return self.name.get("fr", self.name.get("en", self.name.get("rn", "Unknown")))


class ChatSession(models.Model):
    session_id = models.CharField(
        max_length=100, unique=True, verbose_name=_("Session ID")
    )
    user_id = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("User ID")
    )
    language = models.CharField(
        max_length=2,
        choices=[("fr", "Français"), ("rn", "Ikirundi"), ("en", "English")],
        default="fr",
        verbose_name=_("Language"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Chat Session")
        verbose_name_plural = _("Chat Sessions")

    def __str__(self):
        return f"Session {self.session_id} ({self.language})"


class ChatMessage(models.Model):
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("Session"),
    )
    message = models.TextField(verbose_name=_("Message"))
    is_user = models.BooleanField(default=True, verbose_name=_("Is User Message"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Chat Message")
        verbose_name_plural = _("Chat Messages")

    def __str__(self):
        return f"{'User' if self.is_user else 'Bot'}: {self.message[:50]}"


class Agency(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.TextField()

    def __str__(self):
        return self.name


class Appointment(models.Model):
    full_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    time = models.DateTimeField()
    qr_code = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name or 'Anonyme'} - {self.agency.name} - {self.time}"
