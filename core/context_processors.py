from .translations import TRANSLATIONS

def ui_context(request):
    lang = getattr(request, 'site_lang', 'ru')
    return {
        'site_lang': lang,
        'T': TRANSLATIONS.get(lang, TRANSLATIONS['ru']),
    }
