from django.conf import settings


def seo_context(request):
    return {
        "SITE_URL": settings.SITE_URL,
        "SEO_CANONICAL_HOST": settings.SEO_CANONICAL_HOST,
        "SEO_DEFAULT_IMAGE": settings.SEO_DEFAULT_IMAGE,
    }
