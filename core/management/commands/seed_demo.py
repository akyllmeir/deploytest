from datetime import date
from django.core.management.base import BaseCommand
from core.models import Appointment, Doctor, Patient, User


class Command(BaseCommand):
    help = 'Create demo users and data'

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(
            email='admin@clinic.local',
            defaults={'full_name': 'Главный администратор', 'role': User.Role.ADMIN, 'is_staff': True, 'is_superuser': True, 'must_complete_profile': False},
        )
        admin.set_password('Admin123!')
        admin.save()

        doctor_user, _ = User.objects.get_or_create(
            email='doctor@clinic.local',
            defaults={'full_name': 'Д-р Айбек Сагынов', 'role': User.Role.DOCTOR, 'must_complete_profile': False},
        )
        doctor_user.set_password('Doctor123!')
        doctor_user.save()
        doctor, _ = Doctor.objects.get_or_create(user=doctor_user, defaults={'specialization': 'Терапевт', 'experience_years': 7, 'room': '204', 'phone': '+77010000001'})

        patient_user, _ = User.objects.get_or_create(
            email='patient@clinic.local',
            defaults={'full_name': 'Алия Нурланова', 'role': User.Role.PATIENT, 'must_complete_profile': False},
        )
        patient_user.set_password('Patient123!')
        patient_user.save()
        patient, _ = Patient.objects.get_or_create(user=patient_user, defaults={'gender': 'female', 'phone': '+77010000002', 'address': 'Актобе'})

        Appointment.objects.get_or_create(patient=patient, doctor=doctor, date=date.today(), slot='09:00', defaults={'status': Appointment.Status.PENDING})
        self.stdout.write(self.style.SUCCESS('Demo data created.'))
