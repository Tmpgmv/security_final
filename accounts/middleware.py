"""Bridge the Google OAuth login between two origins.

Two hard constraints shape this middleware:

1. Google only accepts redirect URIs on a public top-level domain — raw IPs
   such as ``10.8.0.1`` are rejected by the Cloud Console (only ``localhost``
   and ``127.0.0.1`` are exempt).  A host whose *own* callback is registered
   in the Cloud Console (``settings.SOCIALACCOUNT_DIRECT_LOGIN_HOSTS``,
   e.g. ``localhost:8000``) therefore runs the whole flow on its own address
   and never shows another origin.  Any other host must run the flow on
   ``settings.SOCIALACCOUNT_BASE_URL`` (the ngrok tunnel, whose callback is
   registered).  Login start and callback must also share one origin,
   because django-allauth stashes its OAuth state in the session of whichever
   origin started the flow.
2. A session cookie is scoped to its origin: a session created on the ngrok
   origin does not authenticate the same browser on ``localhost`` or
   ``10.8.0.1``.

So after a successful callback the browser is handed *back* to the address it
actually browses, via ``/accounts/handoff/`` and a signed, short-lived,
single-use token (see ``accounts/handoff.py``).  Concretely, for a request:

* ``/accounts/google/login/`` on a host listed in
  ``SOCIALACCOUNT_DIRECT_LOGIN_HOSTS`` — untouched, the flow stays on the
  user's own address;
* ``/accounts/google/login/`` on any other non-registered host — 302 to the
  registered origin, carrying the original origin along as
  ``?origin=<scheme>://<host>``;
* ``/accounts/google/login/`` *on* the registered origin — once the view
  302's the browser to Google, remember the ``origin`` parameter in an
  HTTP-only cookie scoped to the callback path (the value is validated
  against ``ALLOWED_HOSTS``);
* ``/accounts/google/login/callback/`` on the registered origin — if the
  callback succeeded (302 + authenticated user) and the cookie is present,
  rewrite the final redirect to
  ``<origin>/accounts/handoff/?t=<token>&next=<path>``.

Anything else passes through untouched.
"""

from urllib.parse import urlencode, urlsplit

from django.conf import settings
from django.http import HttpResponseRedirect
from django.http.request import validate_host
from django.urls import reverse

from accounts.handoff import mint_token

GOOGLE_LOGIN_PATH = "/accounts/google/login/"
GOOGLE_CALLBACK_PATH = "/accounts/google/login/callback/"
REDIRECT_STATUSES = (301, 302, 303, 307, 308)

ORIGIN_PARAM = "origin"
ORIGIN_COOKIE = "master_pol_oauth_origin"
ORIGIN_COOKIE_MAX_AGE = 900  # must outlive allauth's 600 s OAuth state


def _request_origin(request) -> str:
    return f"{request.scheme}://{request.get_host()}"


def _allowed_origin(origin: str) -> bool:
    """True when ``origin`` is an http(s) URL on a host we serve."""
    parts = urlsplit(origin)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        return False
    if parts.path not in ("", "/") or parts.query or parts.fragment:
        return False
    # validate_host() expects the hostname without a port.
    return validate_host(parts.hostname, settings.ALLOWED_HOSTS)


class SocialLoginBaseRedirectMiddleware:
    """Keep the OAuth flow on ``settings.SOCIALACCOUNT_BASE_URL`` and, once
    the user is signed in, hand the browser back to the original origin."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        base_url = (getattr(settings, "SOCIALACCOUNT_BASE_URL", "") or "").rstrip("/")
        if not base_url:
            return self.get_response(request)

        base_host = (urlsplit(base_url).hostname or "").lower()
        request_host = (urlsplit("//" + request.get_host()).hostname or "").lower()
        direct_hosts = {
            host.lower()
            for host in getattr(settings, "SOCIALACCOUNT_DIRECT_LOGIN_HOSTS", []) or []
        }

        if (
            request.path == GOOGLE_LOGIN_PATH
            and request.get_host().lower() not in direct_hosts
            and request_host != base_host
        ):
            # (1) Start the flow on the registered origin, telling it where
            # the user came from.
            origin = _request_origin(request)
            target = base_url + request.get_full_path()
            if ORIGIN_PARAM not in request.GET:
                target += ("&" if "?" in target else "?") + urlencode(
                    {ORIGIN_PARAM: origin}
                )
            return HttpResponseRedirect(target)

        response = self.get_response(request)

        if request_host == base_host:
            if request.path == GOOGLE_LOGIN_PATH:
                self._remember_origin(request, response)
            elif request.path == GOOGLE_CALLBACK_PATH:
                self._hand_off(request, response)
        return response

    def _remember_origin(self, request, response) -> None:
        """(2) Park the origin the user started from in a callback-only cookie.

        allauth renders a confirmation page on GET and only afterwards 302's
        to accounts.google.com (the confirmation POST may well drop the
        query string), so the cookie is set on *any* response to the login
        path — it just needs to exist by the time the callback arrives.
        """
        origin = request.GET.get(ORIGIN_PARAM, "")
        if not origin or not _allowed_origin(origin):
            return
        response.set_cookie(
            ORIGIN_COOKIE,
            origin,
            max_age=ORIGIN_COOKIE_MAX_AGE,
            path=GOOGLE_CALLBACK_PATH,
            httponly=True,
            samesite="Lax",
            secure=request.is_secure(),
        )

    def _hand_off(self, request, response) -> None:
        """(3) After a successful login, reroute to the original origin.

        The target carries the one-time token; ``next`` keeps the path the
        user would have landed on (allauth's own redirect target).
        """
        if response.status_code not in REDIRECT_STATUSES:
            return  # login failed/cancelled — nothing to hand off
        origin = request.COOKIES.get(ORIGIN_COOKIE, "")
        if not origin or not _allowed_origin(origin):
            return
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return

        # Where would we have stayed on the registered origin?
        location = response.get("Location", "")
        parts = urlsplit(location)
        next_target = parts.path or "/"
        if parts.query:
            next_target += "?" + parts.query
        if not next_target.startswith("/") or next_target.startswith("//"):
            next_target = "/"

        token = mint_token(user)
        handoff_url = (
            origin.rstrip("/")
            + reverse("accounts_handoff")
            + "?"
            + urlencode({"t": token, "next": next_target})
        )
        response["Location"] = handoff_url
        response.delete_cookie(ORIGIN_COOKIE, path=GOOGLE_CALLBACK_PATH)
