from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Appointment, Doctor, LabResult, Patient, User, AnalysisParameter, AnalysisType, PatientAnalysisFile
from django.contrib.auth.forms import UserCreationForm
from datetime import date


class StyledAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control app-input', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control app-input', 'placeholder': 'Password'}))


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialization', 'experience_years', 'room', 'phone', 'consultation_fee', 'photo']
        widgets = {
            'specialization': forms.TextInput(attrs={'class': 'form-control app-input'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control app-input'}),
            'room': forms.TextInput(attrs={'class': 'form-control app-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-control app-input', 'placeholder': '+77011234567'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control app-input', 'step': '0.01'}),
        }

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()
        if phone.startswith('8') and len(phone) == 11:
            phone = '+7' + phone[1:]
        return phone


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['birth_date', 'gender', 'phone', 'address']
        widgets = {
            'birth_date': forms.DateInput(attrs={'class': 'form-control app-input', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select app-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-control app-input', 'placeholder': '+77011234567'}),
            'address': forms.TextInput(attrs={'class': 'form-control app-input'}),
        }

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()
        if phone.startswith('8') and len(phone) == 11:
            phone = '+7' + phone[1:]
        return phone


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'slot']
        widgets = {
            'doctor': forms.Select(attrs={
                'class': 'form-select app-input'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control app-input',
                'type': 'date'
            }),
            'slot': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        slot_choices = kwargs.pop('slot_choices', [])

        super().__init__(*args, **kwargs)

        self.fields['doctor'].queryset = Doctor.objects.select_related('user').all()
        self.fields['slot'].choices = slot_choices

        self.fields['date'].widget.attrs.update({
            'min': date.today().isoformat(),
            'class': 'form-control app-input',
            'type': 'date'
        })

        self.fields['doctor'].widget.attrs.update({
            'class': 'form-select app-input'
        })

        self.fields['slot'].widget.attrs.update({
            'class': 'form-control app-input'
        })

class AppointmentSummaryForm(forms.Form):
    diagnosis = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control app-input summary-textarea', 'rows': 4}))
    recommendations = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control app-input summary-textarea', 'rows': 4}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control app-input summary-textarea summary-textarea-large', 'rows': 8}))
    medicine_1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control app-input', 'placeholder': 'Название лекарства'}))
    dosage_1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control app-input', 'placeholder': 'При необходимости: доза/количество'}))
    instructions_1 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control app-input prescription-textarea', 'rows': 4, 'placeholder': 'Например: принимать по инструкции, 1/2 порции, после еды и т.п.'}))
    medicine_2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control app-input', 'placeholder': 'Название лекарства'}))
    dosage_2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control app-input', 'placeholder': 'При необходимости: доза/количество'}))
    instructions_2 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control app-input prescription-textarea', 'rows': 4, 'placeholder': 'Например: принимать по инструкции, 1/2 порции, после еды и т.п.'}))
    medicine_3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control app-input', 'placeholder': 'Название лекарства'}))
    dosage_3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control app-input', 'placeholder': 'При необходимости: доза/количество'}))
    instructions_3 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control app-input prescription-textarea', 'rows': 4, 'placeholder': 'Например: принимать по инструкции, 1/2 порции, после еды и т.п.'}))
    medicine_4 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control app-input', 'placeholder': 'Название лекарства'}))
    dosage_4 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control app-input', 'placeholder': 'При необходимости: доза/количество'}))
    instructions_4 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control app-input prescription-textarea', 'rows': 4, 'placeholder': 'Например: принимать по инструкции, 1/2 порции, после еды и т.п.'}))
    medicine_5 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control app-input', 'placeholder': 'Название лекарства'}))
    dosage_5 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control app-input', 'placeholder': 'При необходимости: доза/количество'}))
    instructions_5 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control app-input prescription-textarea', 'rows': 4, 'placeholder': 'Например: принимать по инструкции, 1/2 порции, после еды и т.п.'}))
    recommended_analyses = forms.CharField(
    required=False,
    widget=forms.Textarea(attrs={
        'class': 'form-control app-input',
        'rows': 3,
        'placeholder': 'Жалпы қан анализі\nБиохимия\nЗәр анализі'
    })
)
    recommended_analysis_types = forms.ModelMultipleChoiceField(
        queryset=AnalysisType.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Ұсынылған анализдер'
    )


class LabResultForm(forms.ModelForm):
    class Meta:
        model = LabResult
        fields = ['patient', 'appointment', 'title', 'result_text']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select app-input'}),
            'appointment': forms.Select(attrs={'class': 'form-select app-input'}),
            'title': forms.TextInput(attrs={'class': 'form-control app-input'}),
            'result_text': forms.Textarea(attrs={'class': 'form-control app-input', 'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = Patient.objects.select_related('user').order_by('user__full_name')
        self.fields['appointment'].queryset = Appointment.objects.select_related('patient__user', 'doctor__user').order_by('-date', 'slot')
        if user and getattr(user, 'role', None) == User.Role.DOCTOR and hasattr(user, 'doctor_profile'):
            self.fields['appointment'].queryset = self.fields['appointment'].queryset.filter(doctor=user.doctor_profile)
            patient_ids = self.fields['appointment'].queryset.values_list('patient_id', flat=True)
            self.fields['patient'].queryset = self.fields['patient'].queryset.filter(id__in=patient_ids)


class UserAdminSiteForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control app-input'}))

    class Meta:
        model = User
        fields = ['full_name', 'email', 'role', 'is_active']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control app-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-control app-input'}),
            'role': forms.Select(attrs={'class': 'form-select app-input'}),
            'is_active': forms.Select(choices=((True, 'Активен'), (False, 'Неактивен')), attrs={'class': 'form-select app-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class PatientAnalysisFileForm(forms.ModelForm):
    class Meta:
        model = PatientAnalysisFile
        fields = ['title', 'result_date', 'file', 'note']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control app-input'}),
            'result_date': forms.DateInput(attrs={'class': 'form-control app-input', 'type': 'date'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control app-input'}),
            'note': forms.Textarea(attrs={'class': 'form-control app-input', 'rows': 3}),
        }


class PatientRegisterForm(UserCreationForm):
    full_name = forms.CharField()
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password1', 'password2']

    def __init__(self, *args, T=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['full_name'].label = T.full_name if T else 'Аты-жөні'
        self.fields['email'].label = T.email if T else 'Email'
        self.fields['password1'].label = T.password if T else 'Құпия сөз'
        self.fields['password2'].label = T.password_confirm if T else 'Құпия сөзді қайталау'

        self.fields['full_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': T.full_name_placeholder if T else 'Аты-жөніңізді енгізіңіз'
        })

        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': T.email_placeholder if T else 'Email енгізіңіз'
        })

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': T.password_placeholder if T else 'Құпия сөз енгізіңіз'
        })

        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': T.password_confirm_placeholder if T else 'Құпия сөзді қайталаңыз'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']
        user.role = User.Role.PATIENT
        user.must_complete_profile = True

        if commit:
            user.save()

        return user