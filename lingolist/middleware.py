from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalHostMiddleware:
    """Optional fallback host redirect if the reverse proxy is not enforcing it."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = settings.DJANGO_ENFORCE_CANONICAL_HOST

    def __call__(self, request):
        if self.enabled:
            request_host = request.get_host().split(":")[0].lower()
            request_scheme = "https" if request.is_secure() else "http"

            if (
                request_host != settings.SEO_CANONICAL_HOST
                or request_scheme != "https"
            ):
                redirect_url = f"{settings.SITE_URL}{request.get_full_path()}"
                return HttpResponsePermanentRedirect(redirect_url)

        return self.get_response(request)
