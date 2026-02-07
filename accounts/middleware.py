from django.utils import translation


class UserLanguageMiddleware:
    """
    Middleware to set the user's preferred UI language.

    This must be placed after AuthenticationMiddleware and LocaleMiddleware
    to override the browser-detected language with the user's saved preference.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, "ui_language"):
            user_language = request.user.ui_language
            if user_language:
                translation.activate(user_language)
                request.LANGUAGE_CODE = user_language

        response = self.get_response(request)
        return response
