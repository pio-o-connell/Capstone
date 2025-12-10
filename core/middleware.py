"""Middleware helpers for the core app."""
from __future__ import annotations

from typing import Iterable

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from . import error_views


class CustomErrorPageMiddleware(MiddlewareMixin):
    """Render branded pages for additional HTTP error status codes."""

    HANDLED_STATUSES: Iterable[int] = (405, 408, 502, 503, 504)

    def process_response(self, request, response):  # noqa: D401 - Django signature
        if settings.DEBUG:
            return response

        status_code = getattr(response, 'status_code', None)
        if status_code not in self.HANDLED_STATUSES:
            return response

        if getattr(response, 'streaming', False):
            return response

        new_response = error_views.render_error_page(request, status_code)

        allow_header = None
        if hasattr(response, 'headers'):
            allow_header = response.headers.get('Allow')
        if not allow_header:
            allow_header = response.get('Allow', None)
        if allow_header:
            new_response['Allow'] = allow_header
        return new_response
