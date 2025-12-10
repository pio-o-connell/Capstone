"""Custom error handlers shared across the project."""
from __future__ import annotations

from typing import Any, Dict

from django.conf import settings
from django.shortcuts import render

DEFAULT_TEMPLATE = 'core/errors/error_page.html'

ERROR_PAGE_CONTENT: Dict[int, Dict[str, Any]] = {
    400: {
        'title': 'Bad Request',
        'subtitle': 'The request could not be understood.',
        'image_path': 'core/images/errors/400.jpg',
        'cta_label': 'Return home',
        'cta_url': '/',
    },
    403: {
        'title': 'Forbidden',
        'subtitle': 'You do not have permission to view this resource.',
        'image_path': 'core/images/errors/403.jpg',
        'cta_label': 'Back to safety',
        'cta_url': '/',
    },
    404: {
        'title': 'Page not found',
        'subtitle': 'The page you are looking for moved or never existed.',
        'image_path': 'core/images/errors/404.jpg',
        'cta_label': 'Go to homepage',
        'cta_url': '/',
    },
    405: {
        'title': 'Method not allowed',
        'subtitle': 'The action you attempted is not supported here.',
        'image_path': 'core/images/errors/400.jpg',
        'cta_label': 'Try a different link',
        'cta_url': '/',
    },
    408: {
        'title': 'Request timeout',
        'subtitle': 'This request took too long. Please try again.',
        'image_path': 'core/images/errors/400.jpg',
        'cta_label': 'Reload page',
        'cta_url': '/',
    },
    500: {
        'title': 'Server error',
        'subtitle': 'Something unexpected happened on our side.',
        'image_path': 'core/images/errors/500.jpg',
        'cta_label': 'Return home',
        'cta_url': '/',
    },
    502: {
        'title': 'Bad gateway',
        'subtitle': 'Upstream service responded with an error.',
        'image_path': 'core/images/errors/500.jpg',
        'cta_label': 'Try again shortly',
        'cta_url': '/',
    },
    503: {
        'title': 'Service unavailable',
        'subtitle': 'We are performing maintenance. Please check back soon.',
        'image_path': 'core/images/errors/500.jpg',
        'cta_label': 'Reload page',
        'cta_url': '/',
    },
    504: {
        'title': 'Gateway timeout',
        'subtitle': 'Upstream services took too long to respond.',
        'image_path': 'core/images/errors/500.jpg',
        'cta_label': 'Try again later',
        'cta_url': '/',
    },
}

FALLBACK_CONTENT = {
    'title': 'Unexpected error',
    'subtitle': 'An unexpected issue occurred.',
    'image_path': 'core/images/errors/500.jpg',
    'cta_label': 'Return home',
    'cta_url': '/',
}


def _error_context(status_code: int, extra_context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    context = ERROR_PAGE_CONTENT.get(status_code, FALLBACK_CONTENT).copy()
    context.setdefault('status_code', status_code)
    support_email = getattr(settings, 'SUPPORT_EMAIL', None) or getattr(settings, 'DEFAULT_FROM_EMAIL', None)
    context.setdefault('support_email', support_email)
    if extra_context:
        context.update(extra_context)
    return context


def render_error_page(request, status_code: int, *, extra_context: Dict[str, Any] | None = None):
    context = _error_context(status_code, extra_context)
    return render(
        request,
        context.get('template', DEFAULT_TEMPLATE),
        context,
        status=status_code,
    )


def bad_request(request, exception):
    return render_error_page(request, 400)


def permission_denied(request, exception):
    return render_error_page(request, 403)


def page_not_found(request, exception):
    return render_error_page(request, 404)


def server_error(request):
    return render_error_page(request, 500)


def method_not_allowed(request, exception=None):
    return render_error_page(request, 405)


def request_timeout(request, exception=None):
    return render_error_page(request, 408)


def bad_gateway(request, exception=None):
    return render_error_page(request, 502)


def service_unavailable(request, exception=None):
    return render_error_page(request, 503)


def gateway_timeout(request, exception=None):
    return render_error_page(request, 504)

