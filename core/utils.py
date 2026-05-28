from datetime import time
from .models import Appointment
from django.utils import timezone


DEFAULT_SLOTS = [
    '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
    '14:00', '14:30', '15:00', '15:30', '16:00', '16:30',
]


BLOCKING_STATUSES = [
    Appointment.Status.PENDING,
    Appointment.Status.APPROVED,
    Appointment.Status.COMPLETED,
]

def slot_choices_for_doctor(doctor, date_value):
    return [
        (item['value'], item['label'])
        for item in slot_map_for_doctor(doctor, date_value)
        if item['available']
    ]


def slot_map_for_doctor(doctor, date_value):
    busy_slots = Appointment.objects.filter(
        doctor=doctor,
        date=date_value,
        status__in=BLOCKING_STATUSES,
    ).values_list('slot', flat=True)

    busy = set()

    for slot in busy_slots:
        if isinstance(slot, time):
            busy.add(slot.strftime('%H:%M'))
        else:
            busy.add(str(slot)[:5])

    now = timezone.localtime()
    today = now.date()
    current_time = now.time()

    result = []

    for slot in DEFAULT_SLOTS:
        hh, mm = map(int, slot.split(':'))
        slot_time = time(hour=hh, minute=mm)

        is_busy = slot in busy
        is_past_today = date_value == today and slot_time <= current_time
        is_past_date = date_value < today

        is_free = not is_busy and not is_past_today and not is_past_date

        result.append({
            'value': slot,
            'label': slot,
            'available': is_free
        })

    return result