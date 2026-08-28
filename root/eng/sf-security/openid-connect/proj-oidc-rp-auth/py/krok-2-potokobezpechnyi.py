import json
import time
import urllib.request
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

class JwksManager:
    def __init__(self, jwks_uri: str, ttl_seconds: int = 86400):
        self.jwks_uri = jwks_uri
        self.ttl = ttl_seconds
        self.keys: dict[str, rsa.RSAPublicKey] = {}
        self.last_fetched: float = 0.0
        self.min_refresh_interval: float = 10.0

    @staticmethod
    def _b64url_decode(s: str) -> bytes:
        rem = len(s) % 4
        if rem > 0:
            s += "=" * (4 - rem)
        return base64.urlsafe_b64decode(s.encode('ascii'))

    def _fetch_keys(self) -> None:
        req = urllib.request.Request(
            self.jwks_uri,
            headers={"User-Agent": "OIDC-RelyingParty-Engine/1.0", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                raise RuntimeError(f"Помилка завантаження JWKS: HTTP {response.status}")
            raw_data = response.read().decode('utf-8')
            data = json.loads(raw_data)
            
        new_keys = {}
        for key_data in data.get("keys", []):
            if key_data.get("kty") == "RSA" and key_data.get("use", "sig") == "sig":
                kid = key_data.get("kid")
                if not kid:
                    continue
                # Витягуємо параметри модуля n та експоненти e
                n_bytes = self._b64url_decode(key_data["n"])
                e_bytes = self._b64url_decode(key_data["e"])
                n_int = int.from_bytes(n_bytes, byteorder='big')
                e_int = int.from_bytes(e_bytes, byteorder='big')
                
                pub_num = rsa.RSAPublicNumbers(e_int, n_int)
                pub_key = pub_num.public_key(default_backend())
                new_keys[kid] = pub_key

        self.keys = new_keys
        self.last_fetched = time.time()

    def get_key(self, kid: str) -> rsa.RSAPublicKey:
        now = time.time()
        # Планове оновлення, якщо кеш застарів або ще порожній
        if now - self.last_fetched > self.ttl or not self.keys:
            self._fetch_keys()

        # Якщо kid новий (можлива ротація) — робимо одиночне форсоване оновлення
        if kid not in self.keys:
            if now - self.last_fetched > self.min_refresh_interval:
                self._fetch_keys()
                
        if kid not in self.keys:
            raise KeyError(f"Публічний ключ із kid='{kid}' не знайдено в JWKS провайдера")
            
        return self.keys[kid]
