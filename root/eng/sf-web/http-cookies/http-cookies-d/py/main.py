import urllib.parse
from typing import Optional, Dict

class SessionManager:
    def __init__(self):
        self.session_store: Dict[str, dict] = {}

    def get_cookie(self, cookie_header: Optional[str], name: str) -> Optional[str]:
        """Парсинг cookie з сирого заголовка запиту."""
        if not cookie_header:
            return None

        for part in cookie_header.split(";"):
            part = part.strip()
            if "=" in part:
                k, v = part.split("=", 1)
                if k.strip() == name:
                    return urllib.parse.unquote(v.strip())
        return None

    def create_session_header(self, sid: str) -> str:
        """Генерація Set-Cookie із захисним префіксом __Host-."""
        encoded_sid = urllib.parse.quote(sid, safe="")
        directives = [
            f"__Host-sid={encoded_sid}",
            "Path=/",
            "Max-Age=86400",        # 24 години
            "HttpOnly",             # невидимо для JS
            "Secure",               # тільки HTTPS
            "SameSite=Lax"          # захист від CSRF
        ]
        return "; ".join(directives)

    def create_logout_header(self) -> str:
        """Скидання cookie через нульовий Max-Age."""
        return "__Host-sid=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax"
