"""Minimal CORS for the read-only API.

The storefront (domain.com) calls api.domain.com from the browser for the
vehicle selector and search. The API is public read-only data, so a permissive
allow-origin on /api/ paths only is safe — /admin and everything else stay
same-origin. A 20-line middleware beats another dependency on shared hosting.
"""
from django.conf import settings


class ApiCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/api/") or request.path.startswith("/media/"):
            response["Access-Control-Allow-Origin"] = getattr(
                settings, "CORS_ALLOW_ORIGIN", "*"
            )
            response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
