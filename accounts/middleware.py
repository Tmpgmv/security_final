"""Hand the Google login flow over to a fixed origin.

django-allauth builds the ``redirect_uri`` it sends to Google from the host
that serves ``/accounts/google/login/``.  Only one redirect URI is registered
in the Google Cloud Console:

    https://crook-unfrosted-proponent.ngrok-free.dev/accounts/google/login/callback/

So if the app is opened on any other host (``localhost``, ``10.8.0.1``, ...)
Google rejects the authorization request with a 400.  Redirecting the browser
to the registered origin *before* allauth stashes its OAuth state also keeps
start and callback on the same origin, so the state stored in the session is
still there when Google calls back.
"""

from urllib.parse import urlparse

from django.conf import settings
from django.http import HttpResponseRedirect

GOOGLE_LOGIN_PATH = "/accounts/google/login/"


class SocialLoginBaseRedirectMiddleware:
    """302 the Google login start to ``settings.SOCIALACCOUNT_BASE_URL``.

    A no-op when the setting is empty/falsy or the request already arrives on
    that origin.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        base_url = getattr(settings, "SOCIALACCOUNT_BASE_URL", "") or ""
        if base_url and request.path == GOOGLE_LOGIN_PATH:
            base_host = urlparse(base_url).hostname
            request_host = urlparse("//" + request.get_host()).hostname
            if base_host and request_host and request_host.lower() != base_host.lower():
                return HttpResponseRedirect(
                    base_url.rstrip("/") + request.get_full_path()
                )
        return self.get_response(request)
