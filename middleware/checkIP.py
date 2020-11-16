from django.http import HttpResponse, HttpResponseForbidden
from django.utils.http import is_same_domain
import os


class checkIP:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/api/callback' or request.path.startswith('/api/admin'):
            return self.get_response(request)
        if request.method != 'POST' or os.getenv('CHECK_KEY') not in request.headers or request.headers[os.getenv('CHECK_KEY')] not in os.getenv('CHECK_VALUE').split(';'):
            return HttpResponseForbidden()
        response = self.get_response(request)
        return response