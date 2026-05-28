from datetime import datetime, date, time
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.forms import formset_factory
from django.http import JsonResponse
from django.contrib.auth import login
from .forms import PatientRegisterForm
from .models import (
    AnalysisType,
    AnalysisParameter,
    PatientAnalysisFile,
    PatientAnalysisFile
)
from django.views.decorators.http import require_POST
from openai import OpenAI
from django.conf import settings
from django.db import IntegrityError

from .forms import (
    AppointmentForm,
    AppointmentSummaryForm,
    DoctorProfileForm,
    LabResultForm,
    PatientProfileForm,
    StyledAuthenticationForm,
    UserAdminSiteForm,
    PatientAnalysisFileForm,
)
from .models import Appointment, Doctor, LabResult, MedicalRecord, Patient, Prescription, User
from .utils import slot_choices_for_doctor, slot_map_for_doctor
from .forms import DoctorProfileForm, PatientProfileForm

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def build_system_prompt(user):
    if user.role == 'patient':
        return """
Сен MirraMed медициналық веб-қосымшасының пациентке арналған AI-көмекшісісің.

Міндеттерің:
- сайт бөлімдерін түсіндіру;
- қабылдауға қалай жазылу керегін айту;
- анализ нәтижелері қай жерде екенін түсіндіру;
- медкарта қайда орналасқанын түсіндіру.

Маңызды:
- диагноз қойма;
- дәрі тағайындама;
- қауіпті симптом болса дәрігерге қаралуға кеңес бер.

Тіл:
- Қазақша сұраққа қазақша жауап бер.
- Орысша сұраққа орысша жауап бер.
"""

    if user.role == 'doctor':
        return """
Сен дәрігерге арналған клиникалық AI-көмекшісің.

Жауаптарың:
- өте қысқа;
- нақты;
- құрылымды болуы керек.

Ұзақ түсіндірме жазба.

Жауаптарды міндетті түрде құрылымды форматта жаз.
Формат:

🩺 Ықтимал диагноздар
• ...
• ...

🧪 Ұсынылатын анализдер
• ...
• ...

💊 Ұсынылатын препараттар
• ...
• ...

⚠️ Қауіпті белгілер
• ...
• ...

📌 Ескерту
...

Маңызды:
- соңғы диагнозды тек дәрігер қояды;
- нақты емді дәрігер бекітеді.

Тіл:
- Қазақша сұрақ → қазақша жауап
- Орысша сұрақ → орысша жауап
"""

    if user.role == 'admin':
        return """
Сен MirraMed жүйесінің администраторға арналған AI-көмекшісісің.

Міндеттерің:
- админ панельді түсіндіру;
- қолданушылар, жазылулар, есептер туралы бағыт беру;
- сайт мүмкіндіктерін түсіндіру.

Тіл:
- Қазақша сұраққа қазақша жауап бер.
- Орысша сұраққа орысша жауап бер.
"""

    return """
Сен MirraMed жүйесінің AI-көмекшісісің.
Пайдаланушыға сайт бойынша көмектес.
"""


@login_required
@require_POST
def chatbot_reply(request):

    message = request.POST.get("message", "").strip()

    site_lang = request.session.get('site_lang', 'kz')

    if not message:
        return JsonResponse({
            "reply": (
                "Хабарлама бос."
                if site_lang == 'kz'
                else "Сообщение пустое."
            )
        })

    message_lower = message.lower()

    # 🔥 Fast hybrid replies
    # Пациент пен админ үшін ғана

    if request.user.role != 'doctor':

        if "запис" in message_lower or "жазыл" in message_lower:

            reply = (
                "Қабылдауға жазылу үшін 'Жазылулар' бөлімін ашып, дәрігер мен уақытты таңдаңыз."
                if site_lang == 'kz'
                else "Чтобы записаться на приём, откройте раздел 'Записи', выберите врача и время."
            )

            return JsonResponse({
                "reply": reply
            })

        if "профиль" in message_lower:

            reply = (
                "Профиль бөлімі жоғарғы мәзірде орналасқан."
                if site_lang == 'kz'
                else "Раздел профиля находится в верхнем меню."
            )

            return JsonResponse({
                "reply": reply
            })

        if "анализ" in message_lower:

            reply = (
                "Анализ нәтижелерін 'Анализдер' бөлімінен көре аласыз."
                if site_lang == 'kz'
                else "Результаты анализов можно посмотреть в разделе 'Анализы'."
            )

            return JsonResponse({
                "reply": reply
            })

    # GPT prompt

    system_prompt = build_system_prompt(request.user)

    try:

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": message
                },
            ],
        )

        answer = response.output_text

    except Exception as e:

        print("OPENAI ERROR:", e)

        answer = (
            "AI сервисі уақытша қолжетімсіз. Кейінірек қайталап көріңіз."
            if site_lang == 'kz'
            else "AI-сервис временно недоступен. Попробуйте позже."
        )

    return JsonResponse({
        "reply": answer
    })


def home(request):
    doctors = Doctor.objects.select_related('user').all()[:3]

    return render(request, 'home.html', {
        'doctors': doctors,
    })


class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    authentication_form = StyledAuthenticationForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return CustomLoginView.as_view()(request)


def switch_language(request, lang):
    if lang in {'ru', 'kz'}:
        request.session['site_lang'] = lang
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'
    return redirect(next_url)


@login_required
def dashboard(request):
    if request.user.must_complete_profile and request.user.role != User.Role.ADMIN:
        return redirect('complete_profile')
    if request.user.role == User.Role.ADMIN:
        return redirect('admin_panel')

    appointments = Appointment.objects.none()
    extra = {}
    if request.user.role == User.Role.DOCTOR and hasattr(request.user, 'doctor_profile'):
        doctor = request.user.doctor_profile
        appointments = Appointment.objects.filter(doctor=doctor).select_related('patient__user')[:8]
        extra['lab_results_count'] = LabResult.objects.filter(created_by=request.user).count()
        extra['completed_count'] = Appointment.objects.filter(doctor=doctor, status=Appointment.Status.COMPLETED).count()
    elif request.user.role == User.Role.PATIENT and hasattr(request.user, 'patient_profile'):
        patient = request.user.patient_profile
        appointments = Appointment.objects.filter(patient=patient).select_related('doctor__user')[:8]
        extra['lab_results_count'] = LabResult.objects.filter(patient=patient).count()
        extra['completed_count'] = Appointment.objects.filter(patient=patient, status=Appointment.Status.COMPLETED).count()
    return render(request, 'dashboard.html', {'appointments': appointments, **extra})


@login_required
def complete_profile(request):
    user = request.user
    if user.role == User.Role.DOCTOR:
        profile, _ = Doctor.objects.get_or_create(user=user)
        form_class = DoctorProfileForm
    elif user.role == User.Role.PATIENT:
        profile, _ = Patient.objects.get_or_create(user=user)
        form_class = PatientProfileForm
    else:
        user.must_complete_profile = False
        user.save()
        return redirect('dashboard')

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            user.must_complete_profile = False
            user.save(update_fields=['must_complete_profile'])
            messages.success(request, 'Профиль сохранён.')
            return redirect('dashboard')
    else:
        form = form_class(instance=profile)

    return render(request, 'profile_form.html', {'form': form})


@login_required
def my_profile(request):
    user = request.user

    if user.role == User.Role.DOCTOR:
        profile, _ = Doctor.objects.get_or_create(user=user)
        form_class = DoctorProfileForm
        role_label = 'Дәрігер'
    elif user.role == User.Role.PATIENT:
        profile, _ = Patient.objects.get_or_create(user=user)
        form_class = PatientProfileForm
        role_label = 'Пациент'
    else:
        return redirect('dashboard')

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль жаңартылды.')
            return redirect('my_profile')
    else:
        form = form_class(instance=profile)

    return render(request, 'my_profile.html', {
        'form': form,
        'profile': profile,
        'role_label': role_label,
    })


@login_required
def doctors_list(request):
    # ❌ дәрігерге тыйым
    if request.user.role == 'doctor':
        return redirect('dashboard')  # немесе 'my_profile'
    
    doctors = Doctor.objects.select_related('user').all().order_by('specialization', 'user__full_name')
    return render(request, 'doctors_list.html', {'doctors': doctors})



def _apply_appointment_filters(qs, request):
    sort = request.GET.get('sort', '-date')
    status = request.GET.get('status', '')
    selected_date = request.GET.get('date', '')

    if status:
        qs = qs.filter(status=status)

    if selected_date:
        qs = qs.filter(date=selected_date)

    allowed_sorts = {
        'date': 'date',
        '-date': '-date',
        'slot': 'slot',
        '-slot': '-slot',
        'status': 'status',
        '-status': '-status',
    }
    qs = qs.order_by(allowed_sorts.get(sort, '-date'), 'slot')
    return qs, sort, status, selected_date


@login_required
def appointments_page(request):
    context = {'status_choices': Appointment.Status.choices}

    if request.user.role == User.Role.PATIENT:
        patient = get_object_or_404(Patient, user=request.user)
        appointments = Appointment.objects.filter(patient=patient).select_related('doctor__user')
        appointments, sort, status, selected_date = _apply_appointment_filters(appointments, request)

        selected_doctor_id = request.GET.get('doctor')
        initial = {}
        if selected_doctor_id and Doctor.objects.filter(pk=selected_doctor_id).exists():
            initial['doctor'] = selected_doctor_id

        context.update({
            'appointments': appointments,
            'selected_doctor_id': selected_doctor_id,
            'form': AppointmentForm(slot_choices=[], initial=initial),
            'sort': sort,
            'status_filter': status,
            'date_filter': selected_date,
        })

    elif request.user.role == User.Role.DOCTOR:
        doctor = get_object_or_404(Doctor, user=request.user)

        selected_date = request.GET.get('date')
        if not selected_date:
            selected_date = date.today().isoformat()

        appointments = Appointment.objects.filter(
            doctor=doctor
        ).select_related('patient__user', 'doctor__user')

        mutable_get = request.GET.copy()
        mutable_get['date'] = selected_date
        request.GET = mutable_get

        appointments, sort, status, selected_date = _apply_appointment_filters(appointments, request)

        context.update({
            'appointments': appointments,
            'sort': sort,
            'status_filter': status,
            'date_filter': selected_date,
        })

    else:
        appointments = Appointment.objects.select_related('doctor__user', 'patient__user')
        appointments, sort, status, selected_date = _apply_appointment_filters(appointments, request)
        context.update({
            'appointments': appointments,
            'sort': sort,
            'status_filter': status,
            'date_filter': selected_date,
        })

    return render(request, 'appointments.html', context)


@login_required
@user_passes_test(lambda u: u.role == User.Role.PATIENT)
def create_appointment(request):
    patient = get_object_or_404(Patient, user=request.user)
    site_lang = request.session.get('site_lang', 'kz')

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        date_str = request.POST.get('date')
        slot = request.POST.get('slot')

        if not doctor_id or not date_str or not slot:
            messages.error(
                request,
                'Дәрігер, күн және уақытты таңдаңыз.'
                if site_lang == 'kz'
                else 'Выберите врача, дату и время.'
            )
            return redirect('appointments')

        try:
            doctor = Doctor.objects.get(pk=doctor_id)
            date_value = datetime.strptime(date_str, '%Y-%m-%d').date()
        except Exception:
            messages.error(
                request,
                'Қате мәлімет енгізілді.'
                if site_lang == 'kz'
                else 'Некорректные данные.'
            )
            return redirect('appointments')

        now = timezone.localtime()
        today = now.date()

        if date_value < today:
            messages.error(
                request,
                'Өткен күнге жазылуға болмайды.'
                if site_lang == 'kz'
                else 'Нельзя записаться на прошедшую дату.'
            )
            return redirect('appointments')

        try:
            slot_hour, slot_minute = map(int, slot.split(':'))
            slot_time = time(hour=slot_hour, minute=slot_minute)
        except Exception:
            messages.error(
                request,
                'Қате уақыт таңдалды.'
                if site_lang == 'kz'
                else 'Некорректное время.'
            )
            return redirect('appointments')

        if date_value == today and slot_time <= now.time():
            messages.error(
                request,
                'Өтіп кеткен уақытқа жазылуға болмайды.'
                if site_lang == 'kz'
                else 'Нельзя записаться на прошедшее время.'
            )
            return redirect('appointments')

        available_slots = [
            value for value, label in slot_choices_for_doctor(doctor, date_value)
        ]

        if slot not in available_slots:
            messages.error(
                request,
                'Бұл уақыт бос емес немесе қолжетімсіз.'
                if site_lang == 'kz'
                else 'Это время занято или недоступно.'
            )
            return redirect('appointments')

        blocking_statuses = [
            Appointment.Status.PENDING,
            Appointment.Status.APPROVED,
            Appointment.Status.COMPLETED,
        ]

        slot_taken = Appointment.objects.filter(
            doctor=doctor,
            date=date_value,
            slot=slot_time,
            status__in=blocking_statuses
        ).exists()

        if slot_taken:
            messages.error(
                request,
                'Бұл уақыт бос емес.'
                if site_lang == 'kz'
                else 'Это время уже занято.'
            )
            return redirect('appointments')

        free_statuses = [
            Appointment.Status.REJECTED,
            Appointment.Status.CANCELLED,
            Appointment.Status.NO_SHOW,
        ]

        old_appointment = Appointment.objects.filter(
            doctor=doctor,
            date=date_value,
            slot=slot_time,
            status__in=free_statuses
        ).order_by('-id').first()

        if old_appointment:
            old_appointment.patient = patient
            old_appointment.status = Appointment.Status.PENDING
            old_appointment.fee = doctor.consultation_fee
            old_appointment.approved_at = None
            old_appointment.save(update_fields=[
                'patient',
                'status',
                'fee',
                'approved_at',
            ])
        else:
            Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date=date_value,
                slot=slot_time,
                fee=doctor.consultation_fee,
                status=Appointment.Status.PENDING
            )

        messages.success(
            request,
            'Жазылу жасалды. Дәрігердің растауын күтіңіз.'
            if site_lang == 'kz'
            else 'Запись создана. Ожидайте подтверждения врача.'
        )

    return redirect('appointments')

@login_required
def approve_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    if request.user.role != User.Role.DOCTOR or appointment.doctor.user != request.user:
        return redirect('appointments')
    appointment.status = Appointment.Status.APPROVED
    appointment.approved_at = timezone.now()
    appointment.save(update_fields=['status', 'approved_at'])
    messages.success(request, 'Запись подтверждена.')
    return redirect('appointments')


@login_required
def reject_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    if request.user.role == User.Role.DOCTOR and appointment.doctor.user == request.user:
        appointment.status = Appointment.Status.REJECTED
        appointment.save(update_fields=['status'])
        messages.success(request, 'Запись отклонена.')
    elif request.user.role == User.Role.PATIENT and appointment.patient.user == request.user:
        appointment.status = Appointment.Status.CANCELLED
        appointment.save(update_fields=['status'])
        messages.success(request, 'Запись отменена.')
    return redirect('appointments')


@login_required
def no_show_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    if request.user.role == User.Role.DOCTOR and appointment.doctor.user == request.user:
        appointment.status = Appointment.Status.NO_SHOW
        appointment.save(update_fields=['status'])
        messages.success(request, 'Отмечено: пациент не пришёл.')
    return redirect('appointments')


@login_required
def complete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)

    if request.user.role != User.Role.DOCTOR or appointment.doctor.user != request.user:
        return redirect('appointments')

    # 🆕 Пациент анализдері
    analysis_files = PatientAnalysisFile.objects.filter(
        patient=appointment.patient
    ).order_by('-result_date')

    if request.method == 'POST':
        form = AppointmentSummaryForm(request.POST)

        if form.is_valid():
            record, _ = MedicalRecord.objects.get_or_create(appointment=appointment)

            record.diagnosis = form.cleaned_data['diagnosis']
            record.recommendations = form.cleaned_data['recommendations']
            record.notes = form.cleaned_data['notes']

            # 🆕 Анализ ұсынысы
            record.recommended_analyses = form.cleaned_data.get('recommended_analyses', '')

            record.save()

            record.recommended_analysis_types.set(
                form.cleaned_data.get('recommended_analysis_types')
            )

            record.prescriptions.all().delete()

            for idx in range(1, 6):
                medicine = form.cleaned_data.get(f'medicine_{idx}')
                dosage = form.cleaned_data.get(f'dosage_{idx}')
                instructions = form.cleaned_data.get(f'instructions_{idx}')

                if medicine:
                    Prescription.objects.create(
                        medical_record=record,
                        medicine=medicine,
                        dosage=dosage or '',
                        instructions=instructions or ''
                    )

            appointment.status = Appointment.Status.COMPLETED
            appointment.save(update_fields=['status'])

            messages.success(request, 'Итог приёма сохранён.')
            return redirect('medical_records')

    else:
        initial = {}

        if hasattr(appointment, 'medical_record'):
            record = appointment.medical_record

            initial = {
                'diagnosis': record.diagnosis,
                'recommendations': record.recommendations,
                'notes': record.notes,
                'recommended_analyses': getattr(record, 'recommended_analyses', ''),
                'recommended_analysis_types': record.recommended_analysis_types.all(),
            }

            pres = list(record.prescriptions.all()[:5])

            for i, p in enumerate(pres, start=1):
                initial[f'medicine_{i}'] = p.medicine
                initial[f'dosage_{i}'] = p.dosage
                initial[f'instructions_{i}'] = p.instructions

        form = AppointmentSummaryForm(initial=initial)

    return render(request, 'complete_appointment.html', {
        'form': form,
        'appointment': appointment,
        'analysis_files': analysis_files,  # 🆕 ОСЫ ЖЕР МАҢЫЗДЫ
    })

@login_required
def medical_records_page(request):
    if request.user.role == User.Role.DOCTOR:
        doctor = get_object_or_404(Doctor, user=request.user)
        records = MedicalRecord.objects.filter(appointment__doctor=doctor)
    elif request.user.role == User.Role.PATIENT:
        patient = get_object_or_404(Patient, user=request.user)
        records = MedicalRecord.objects.filter(appointment__patient=patient)
    else:
        records = MedicalRecord.objects.all()
    records = records.select_related('appointment__patient__user', 'appointment__doctor__user').prefetch_related('prescriptions')
    return render(request, 'medical_records.html', {'records': records})


@login_required
def lab_results_page(request):
    if request.user.role == User.Role.PATIENT:
        patient = get_object_or_404(Patient, user=request.user)
        results = LabResult.objects.filter(patient=patient).select_related('created_by', 'appointment__doctor__user')
        form = None
    else:
        results = LabResult.objects.select_related('patient__user', 'created_by', 'appointment__doctor__user')
        form = LabResultForm(user=request.user)
        if request.method == 'POST' and request.user.role in {User.Role.DOCTOR, User.Role.ADMIN}:
            form = LabResultForm(request.POST, user=request.user)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.created_by = request.user
                obj.save()
                messages.success(request, 'Результат анализа отправлен пациенту.')
                return redirect('lab_results')
    return render(request, 'lab_results.html', {'results': results, 'form': form})


@login_required
@user_passes_test(lambda u: u.role == User.Role.ADMIN)
def admin_panel(request):
    users_qs = User.objects.all().order_by('-id')
    editing_user = None
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        editing_user = User.objects.filter(pk=user_id).first() if user_id else None
        form = UserAdminSiteForm(request.POST, instance=editing_user)
        if form.is_valid():
            user = form.save()
            if user.role == User.Role.DOCTOR:
                Doctor.objects.get_or_create(user=user)
            elif user.role == User.Role.PATIENT:
                Patient.objects.get_or_create(user=user)
            messages.success(request, 'Пользователь сохранён.')
            return redirect('admin_panel')
    else:
        edit_id = request.GET.get('edit')
        editing_user = User.objects.filter(pk=edit_id).first() if edit_id else None
        form = UserAdminSiteForm(instance=editing_user)

    stats = {
        'users_count': User.objects.count(),
        'patients_count': User.objects.filter(role='patient').count(),
        'doctors_count': User.objects.filter(role='doctor').count(),
        'appointments_count': Appointment.objects.count(),
        'income_total': Appointment.objects.filter(status=Appointment.Status.COMPLETED).aggregate(total=Sum('fee'))['total'] or Decimal('0.00'),
    }
    appointments_by_status = Appointment.objects.values('status').annotate(total=Count('id')).order_by('status')
    users = users_qs[:25]
    return render(request, 'admin_panel.html', {'stats': stats, 'users': users, 'form': form, 'editing_user': editing_user, 'appointments_by_status': appointments_by_status})


@login_required
def doctor_slots_api(request):
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    if not doctor_id or not date_str:
        return JsonResponse({'slots': []})
    try:
        doctor = Doctor.objects.get(pk=doctor_id)
        date_value = datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        return JsonResponse({'slots': []})
    return JsonResponse({'slots': slot_map_for_doctor(doctor, date_value)})

from .forms import PatientAnalysisFileForm
from .models import PatientAnalysisFile


@login_required
def my_analysis_files(request):
    if request.user.role != 'patient':
        return redirect('dashboard')

    patient = request.user.patient_profile

    if request.method == 'POST':
        form = PatientAnalysisFileForm(request.POST, request.FILES)
        if form.is_valid():
            analysis_file = form.save(commit=False)
            analysis_file.patient = patient
            analysis_file.save()
            messages.success(request, 'Анализ файлы жүктелді.')
            return redirect('my_analysis_files')
    else:
        form = PatientAnalysisFileForm()

    files = PatientAnalysisFile.objects.filter(patient=patient).order_by('-result_date')

    return render(request, 'my_analysis_files.html', {
        'form': form,
        'files': files,
    })


from .translations import TRANSLATIONS

def register(request):
    site_lang = request.session.get('site_lang', 'kz')
    T = type('T', (), TRANSLATIONS[site_lang])

    if request.method == 'POST':
        form = PatientRegisterForm(request.POST, T=T)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('complete_profile')
    else:
        form = PatientRegisterForm(T=T)

    return render(request, 'auth/register.html', {
        'form': form
    })


from django.template.loader import get_template
from django.conf import settings
from .models import Appointment


@login_required
def reports(request):
    if request.user.role != 'admin':
        return redirect('dashboard')

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    today = date.today()

    if date_from:
        date_from_value = datetime.strptime(date_from, '%Y-%m-%d').date()

        if date_from_value > today:
            messages.error(request, 'Дата начала не может быть позже сегодняшнего дня.')
            return redirect('reports')
    else:
        date_from_value = None

    if date_to:
        date_to_value = datetime.strptime(date_to, '%Y-%m-%d').date()

        if date_to_value > today:
            messages.error(request, 'Дата окончания не может быть позже сегодняшнего дня.')
            return redirect('reports')
    else:
        date_to_value = None

    if date_from_value and date_to_value and date_from_value > date_to_value:
        messages.error(request, 'Дата начала не может быть позже даты окончания.')
        return redirect('reports')

    appointments = Appointment.objects.filter(status='completed')

    if date_from_value:
        appointments = appointments.filter(date__gte=date_from_value)

    if date_to_value:
        appointments = appointments.filter(date__lte=date_to_value)

    appointments = appointments.select_related(
        'patient__user',
        'doctor__user'
    ).order_by('-date', '-slot')

    total_income = appointments.aggregate(total=Sum('fee'))['total'] or 0
    completed_count = appointments.count()
    patients_count = appointments.values('patient').distinct().count()

    doctor_income = appointments.values(
        'doctor__user__full_name'
    ).annotate(
        appointments_count=Count('id'),
        total_income=Sum('fee')
    ).order_by('-total_income')

    return render(request, 'reports.html', {
        'date_from': date_from,
        'date_to': date_to,
        'appointments': appointments,
        'total_income': total_income,
        'completed_count': completed_count,
        'patients_count': patients_count,
        'doctor_income': doctor_income,
        'today': today.isoformat(),
    })

