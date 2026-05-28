from django import template

register = template.Library()

STATUS_LABELS = {
    'ru': {'pending': 'ОЖИДАЕТ', 'approved': 'ПОДТВЕРЖДЕНО', 'rejected': 'ОТКЛОНЕНО', 'completed': 'ЗАВЕРШЕНО', 'cancelled': 'ОТМЕНЕНО', 'no_show': 'НЕ ЯВИЛСЯ'},
    'kz': {'pending': 'КҮТУДЕ', 'approved': 'РАСТАЛДЫ', 'rejected': 'БАС ТАРТЫЛДЫ', 'completed': 'АЯҚТАЛДЫ', 'cancelled': 'БАС ТАРТТЫ', 'no_show': 'КЕЛМЕДІ'},
}
STATUS_CLASSES = {'pending': 'status-pending', 'approved': 'status-approved', 'rejected': 'status-rejected', 'completed': 'status-completed', 'cancelled': 'status-cancelled', 'no_show': 'status-no-show'}

@register.filter
def status_label(status, lang='ru'):
    return STATUS_LABELS.get(lang, STATUS_LABELS['ru']).get(status, str(status).upper())

@register.filter
def status_class(status):
    return STATUS_CLASSES.get(status, 'status-pending')
