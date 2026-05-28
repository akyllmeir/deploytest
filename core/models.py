from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r'^(?:\+7\d{10}|8\d{10}|\+[1-9]\d{7,14})$',
    message='Введите номер в формате +77011234567, 87011234567 или в международном формате.'
)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        DOCTOR = 'doctor', 'Doctor'
        PATIENT = 'patient', 'Patient'

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)
    must_complete_profile = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        self.username = self.email
        if self.role == self.Role.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name or self.email


class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=255, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    room = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=30, blank=True, validators=[phone_validator])
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=15000)
    photo = models.ImageField(upload_to='doctors/', null=True, blank=True)

    def __str__(self):
        return f'{self.user.full_name} ({self.specialization})'


class Patient(models.Model):
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female')]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    phone = models.CharField(max_length=30, blank=True, validators=[phone_validator])
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.full_name


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        NO_SHOW = 'no_show', 'No show'

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    slot = models.TimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date', 'slot']
        constraints = [
            models.UniqueConstraint(fields=['doctor', 'date', 'slot'], name='unique_doctor_slot')
        ]

    def save(self, *args, **kwargs):
        if not self.fee and self.doctor_id:
            self.fee = self.doctor.consultation_fee
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.patient} -> {self.doctor} {self.date} {self.slot}'

class AnalysisType(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name_kz = models.CharField(max_length=255, unique=True)
    name_ru = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name_kz

class MedicalRecord(models.Model):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='medical_record'
    )

    diagnosis = models.TextField()
    recommendations = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    # 🆕 Анализ ұсынысы
    recommended_analyses = models.TextField(blank=True)
    recommended_analysis_types = models.ManyToManyField(
    AnalysisType,
    blank=True,
    related_name='medical_records'
)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'MedicalRecord #{self.id}'


class Prescription(models.Model):
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions')
    medicine = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255, blank=True)
    instructions = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.medicine


class LabResult(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_results')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_results')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_lab_results')
    title = models.CharField(max_length=255)
    result_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title



class AnalysisParameter(models.Model):
    class ValueType(models.TextChoices):
        NUMERIC = 'numeric', 'Numeric'
        BOOLEAN = 'boolean', 'Boolean'
        TEXT = 'text', 'Text'

    analysis_type = models.ForeignKey(
        AnalysisType,
        on_delete=models.CASCADE,
        related_name='parameters'
    )

    code = models.CharField(max_length=100)
    name_kz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    unit = models.CharField(max_length=50, blank=True)

    value_type = models.CharField(
        max_length=20,
        choices=ValueType.choices,
        default=ValueType.NUMERIC
    )

    class Meta:
        ordering = ['analysis_type', 'name_kz']
        unique_together = ('analysis_type', 'code')

    def __str__(self):
        return f'{self.analysis_type.name_kz} - {self.name_kz}'


class PatientAnalysisFile(models.Model):
    patient = models.ForeignKey(
        'Patient',
        on_delete=models.CASCADE,
        related_name='analysis_files'
    )
    title = models.CharField(max_length=255)
    result_date = models.DateField()
    file = models.FileField(upload_to='patient_analysis/')
    note = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.patient.user.full_name} - {self.title}'
