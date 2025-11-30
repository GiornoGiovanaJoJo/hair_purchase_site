"""
Context processors for templates
"""
from django.conf import settings


def yandex_metrika(request):
    """
    Add Yandex Metrika ID to template context.
    """
    return {
        'YANDEX_METRIKA_ID': settings.YANDEX_METRIKA_ID
    }
