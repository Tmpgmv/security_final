"""One-time handoff tokens: ngrok origin -> original origin.

After Google's callback completes on ``settings.SOCIALACCOUNT_BASE_URL`` (the
only origin Google accepts as a redirect URI), the browser must come back to
the address the user actually browses (``localhost`` in development,
``10.8.0.1`` over the VPN in production).  The session cookie cannot travel
between origins, so the callback response carries a signed token; the
``/accounts/handoff/`` view on the original origin consumes it and creates a
fresh session there.

The token is a ``TimestampSigner`` payload ``"<user pk>:<nonce>"``:

* signed with ``SECRET_KEY`` and a dedicated salt — cannot be forged;
* time-limited by ``SOCIALACCOUNT_HANDOFF_MAX_AGE`` seconds;
* single-use — the nonce is entered into the cache on first consumption, so
  a captured redirect URL cannot be replayed.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.core.cache import cache
from django.utils.crypto import get_random_string

HANDOFF_SALT = "accounts.handoff"


def _max_age() -> int:
    return int(getattr(settings, "SOCIALACCOUNT_HANDOFF_MAX_AGE", 300))


def mint_token(user) -> str:
    """Return a fresh signed token granting a handoff session for ``user``."""
    nonce = get_random_string(24)
    payload = f"{user.pk}:{nonce}"
    return signing.TimestampSigner(salt=HANDOFF_SALT).sign(payload)


def consume_token(token: str):
    """Validate ``token`` once; return the user, or ``(None, error message)``.

    Returns ``(user, None)`` on success and ``(None, "<reason>")`` when the
    token is forged, expired, already used, or names a missing/disabled user.
    """
    try:
        payload = signing.TimestampSigner(salt=HANDOFF_SALT).unsign(
            token, max_age=_max_age()
        )
        user_pk, nonce = payload.split(":", 1)
    except signing.BadSignature:  # SignatureExpired subclasses BadSignature
        return None, "invalid or expired handoff token"
    except ValueError:
        return None, "malformed handoff token"

    # cache.add() is atomic: the first call wins, replays are rejected.
    if not cache.add(f"accounts-handoff:{nonce}", 1, timeout=_max_age()):
        return None, "handoff token already used"

    user = get_user_model().objects.filter(pk=user_pk, is_active=True).first()
    if user is None:
        return None, "unknown or disabled user"
    return user, None
