import os
import time
import base64
import hashlib
import secrets
import hmac
import urllib.parse
import json
import urllib.request
from typing import Optional, Dict, Any, Tuple

class OAuthClient:
    def __init__(
        self,
        auth_server_url: str,
        client_id: str,
        redirect_uri: str,
        client_secret: Optional[str] = None,
        clock_skew_seconds: int = 60
    ):
        self.auth_server_url = auth_server_url.rstrip("/")
        self.authorize_endpoint = f"{self.auth_server_url}/oauth/authorize"
        self.token_endpoint = f"{self.auth_server_url}/oauth/token"
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.clock_skew = clock_skew_seconds
        
        # Сховище токенів поточної сесії
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.expires_at: float = 0.0
        self.granted_scopes: str = ""
        
        # Тимчасовий стан між перенаправленням і callback
        self._pending_verifier: Optional[str] = None
        self._pending_state: Optional[str] = None

    @staticmethod
    def _base64url_encode(data: bytes) -> str:
        """Кодування байтів у рядок Base64URL без знаків паддингу '='."""
        return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

    def generate_pkce_pair(self) -> Tuple[str, str]:
        """Генерує випадковий code_verifier і відповідний SHA256 code_challenge."""
        # 64 випадкові байти дають 86 символів у base64url (у межах норми 43..128)
        raw_bytes = secrets.token_bytes(64)
        verifier = self._base64url_encode(raw_bytes)
        
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        challenge = self._base64url_encode(digest)
        return verifier, challenge

    def create_authorization_url(self, scopes: list[str]) -> str:
        """Створює повний URL для перенаправлення браузера користувача."""
        verifier, challenge = self.generate_pkce_pair()
        state = self._base64url_encode(secrets.token_bytes(32))
        
        self._pending_verifier = verifier
        self._pending_state = state
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256"
        }
        return f"{self.authorize_endpoint}?{urllib.parse.urlencode(params)}"

    def handle_callback(self, query_params: Dict[str, str]) -> Dict[str, Any]:
        """Обробляє параметри повернення браузера та обмінює код на токени."""
        if "error" in query_params:
            err = query_params.get("error")
            desc = query_params.get("error_description", "Немає опису")
            raise PermissionError(f"Сервер авторизації відхилив запит: {err} ({desc})")
        
        returned_state = query_params.get("state", "")
        if not self._pending_state or not hmac.compare_digest(self._pending_state, returned_state):
            raise SecurityError("Атака підробки запиту: параметр state не збігається!")
            
        code = query_params.get("code")
        if not code:
            raise ValueError("Відповідь авторизації не містить коду (code)")
            
        if not self._pending_verifier:
            raise RuntimeError("Втрачено стан PKCE verifier для цієї сесії")
            
        # Бек-канал: прямий обмін на токени
        tokens = self._exchange_code_for_tokens(code, self._pending_verifier)
        
        # Очищення тимчасового стану після успішного використання
        self._pending_verifier = None
        self._pending_state = None
        
        return tokens

    def _exchange_code_for_tokens(self, code: str, verifier: str) -> Dict[str, Any]:
        """Надсилає HTTP POST на /token для обміну code на токени."""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "code_verifier": verifier
        }
        return self._send_token_request(data)

    def refresh_access_token(self) -> Dict[str, Any]:
        """Використовує refresh_token для отримання нової пари токенів."""
        if not self.refresh_token:
            raise ValueError("Відсутній refresh_token для оновлення сесії")
            
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id
        }
        return self._send_token_request(data)

    def _send_token_request(self, form_data: Dict[str, str]) -> Dict[str, Any]:
        """Виконує прямий мережевий POST-запит до ендпоінта видачі токенів."""
        encoded_data = urllib.parse.urlencode(form_data).encode("utf-8")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        # Автентифікація конфіденційного клієнта через заголовок Basic Auth
        if self.client_secret:
            auth_str = f"{self.client_id}:{self.client_secret}"
            b64_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
            headers["Authorization"] = f"Basic {b64_auth}"
            
        req = urllib.request.Request(self.token_endpoint, data=encoded_data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise RuntimeError(f"Помилка ендпоінта /token [{e.code}]: {err_body}") from e
            
        # Збереження отриманих токенів у пам'яті клієнта
        self.access_token = payload["access_token"]
        # При ротації токенів сервер видає новий refresh_token
        if "refresh_token" in payload:
            self.refresh_token = payload["refresh_token"]
            
        expires_in = payload.get("expires_in", 3600)
        self.expires_at = time.time() + float(expires_in)
        self.granted_scopes = payload.get("scope", "")
        
        return payload

    def get_valid_access_token(self) -> str:
        """Повертає дійсний access_token, автоматично оновлюючи його за потреби."""
        # Оновлюємо заздалегідь (за clock_skew секунд до фактичного закінчення)
        if time.time() >= (self.expires_at - self.clock_skew):
            if self.refresh_token:
                self.refresh_access_token()
            else:
                raise PermissionError("Access token протерміновано, а refresh_token відсутній")
                
        if not self.access_token:
            raise PermissionError("Клієнт ще не пройшов авторизацію")
            
        return self.access_token
