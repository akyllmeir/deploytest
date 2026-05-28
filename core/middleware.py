class SessionLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.session.get('site_lang', 'ru')
        request.site_lang = lang if lang in {'ru', 'kz'} else 'ru'
        response = self.get_response(request)
        return response
