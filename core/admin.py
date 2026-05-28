from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Appointment, Doctor, LabResult, MedicalRecord, Patient, Prescription, User

class DoctorInline(admin.StackedInline):
    model = Doctor
    can_delete = False
    extra = 0

class PatientInline(admin.StackedInline):
    model = Patient
    can_delete = False
    extra = 0

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'role', 'must_complete_profile', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    ordering = ('email',)
    search_fields = ('email', 'full_name')
    fieldsets = ((None, {'fields': ('email', 'password')}), ('Personal info', {'fields': ('full_name', 'role', 'must_complete_profile')}), ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}), ('Important dates', {'fields': ('last_login', 'date_joined')}),)
    add_fieldsets = ((None, {'classes': ('wide',), 'fields': ('email', 'full_name', 'role', 'password1', 'password2', 'is_staff', 'is_active')}),)
    def get_inlines(self, request, obj):
        if not obj:
            return []
        if obj.role == User.Role.DOCTOR:
            return [DoctorInline]
        if obj.role == User.Role.PATIENT:
            return [PatientInline]
        return []

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'experience_years', 'room', 'phone', 'consultation_fee')
    search_fields = ('user__full_name', 'specialization')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'gender', 'phone')
    search_fields = ('user__full_name', 'phone')

class PrescriptionInline(admin.TabularInline):
    model = Prescription
    extra = 0

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'created_at')
    inlines = [PrescriptionInline]

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'slot', 'status', 'fee')
    list_filter = ('status', 'date')
    search_fields = ('patient__user__full_name', 'doctor__user__full_name')

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'dosage', 'instructions', 'medical_record')

@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'patient__user__full_name', 'result_text')
