# cookie_engine.py
from datetime import datetime, timezone
import urllib.parse
import hmac
import hashlib
import re
from typing import Optional, Dict

class CookieError(ValueError):
    """Помилка валідації або серіалізації параметрів cookie."""
    pass

def parse_cookies(header: Optional[str]) -> Dict[str, str]:
    """Стійкий парсер вхідного заголовка Cookie відповідно до RFC 6265."""
    cookies: Dict[str, str] = {}
    if not header:
        return cookies

    for item in header.split(";"):
        item = item.strip()
        if not item:
            continue

        if "=" in item:
            key, val = item.split("=", 1)
            key = key.strip()
            val = val.strip()

            # Зняти обрамляючі подвійні лапки
            if len(val) >= 2 and val.startswith('"') and val.endswith('"'):
                val = val[1:-1]

            decoded_key = urllib.parse.unquote(key)
            decoded_val = urllib.parse.unquote(val)
            if decoded_key and decoded_key not in cookies:
                cookies[decoded_key] = decoded_val
        else:
            decoded_key = urllib.parse.unquote(item)
            if decoded_key and decoded_key not in cookies:
                cookies[decoded_key] = ""

    return cookies

def serialize_set_cookie(
    name: str,
    value: str,
    *,
    max_age: Optional[int] = None,
    expires: Optional[datetime] = None,
    domain: Optional[str] = None,
    path: Optional[str] = None,
    secure: bool = False,
    http_only: bool = False,
    same_site: Optional[str] = None,
    partitioned: bool = False
) -> str:
    """Серіалізатор Set-Cookie з валідацією префіксів __Host- та __Secure-."""
    if not name or not re.match(r"^[\x21-\x3A\x3C\x7E]+$", name):
        raise CookieError(f"Неприпустимі символи в імені cookie: '{name}'")

    # Валідація захисних префіксів RFC 6265bis
    if name.startswith("__Secure-"):
        if not secure:
            raise CookieError("Префікс __Secure- вимагає secure=True")

    if name.startswith("__Host-"):
        if not secure:
            raise CookieError("Префікс __Host- вимагає secure=True")
        if domain:
            raise CookieError("Префікс __Host- категорично забороняє атрибут domain")
        if path != "/":
            raise CookieError("Префікс __Host- обов'язково вимагає path='/'")

    encoded_val = urllib.parse.quote(value, safe="")
    parts = [f"{name}={encoded_val}"]

    if max_age is not None:
        parts.append(f"Max-Age={int(max_age)}")

    if domain:
        parts.append(f"Domain={domain}")

    if path:
        parts.append(f"Path={path}")

    if expires:
        # Форматування дати за RFC 1123 в зоні UTC
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        gmt_str = expires.astimezone(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        parts.append(f"Expires={gmt_str}")

    if http_only:
        parts.append("HttpOnly")

    if secure:
        parts.append("Secure")

    if same_site:
        mode = same_site.capitalize()
        if mode not in ("Strict", "Lax", "None"):
            raise CookieError(f"Невідомий режим SameSite: '{same_site}'")
        if mode == "None" and not secure:
            raise CookieError("SameSite=None обов'язково вимагає secure=True")
        parts.append(f"SameSite={mode}")

    if partitioned:
        parts.append("Partitioned")

    return "; ".join(parts)

def verify_signed_cookie(signed_value: str, secret: str) -> Optional[str]:
    """Перевірка підпису HMAC у константному часі для захисту від Timing Attacks."""
    if "." not in signed_value:
        return None
    val, sig = signed_value.rsplit(".", 1)
    expected_sig = hmac.new(secret.encode(), val.encode(), hashlib.sha256).hexdigest()
    if hmac.compare_digest(sig, expected_sig):
        return val
    return None
