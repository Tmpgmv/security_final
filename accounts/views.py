from django.contrib.auth import login as auth_login
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render

from .handoff import consume_token

# The backend django-allauth authenticates social users with; recorded in the
# new session so later requests can restore the user.
ALLAUTH_BACKEND = "allauth.account.auth_backends.AuthenticationBackend"


def handoff(request):
    """Establish a session on the origin the user actually browses.

    Reached only from the registered OAuth origin (see
    ``accounts.middleware``) after a successful Google login, with
    ``?t=<one-time token>&next=<path>``.  Consumes the token, logs the user
    in on *this* origin and continues to ``next``.
    """
    token = request.GET.get("t", "")
    next_url = request.GET.get("next", "/")

    user, error = consume_token(token)
    if user is None:
        return HttpResponseBadRequest(f"Handoff failed: {error}")

    # ``next`` only ever comes from a redirect we built ourselves; still,
    # allow local paths only so this cannot become an open redirect.
    if not next_url.startswith("/") or next_url.startswith("//"):
        next_url = "/"

    auth_login(request, user, backend=ALLAUTH_BACKEND)
    return HttpResponseRedirect(next_url)
