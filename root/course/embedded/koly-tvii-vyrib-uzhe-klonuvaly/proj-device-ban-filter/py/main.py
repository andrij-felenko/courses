import hmac
import time
import secrets
from typing import Dict, Optional, Tuple, Set
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key

class AttestationSecurityGateway:
    def __init__(self, hmac_signing_key: bytes, challenge_ttl_sec: float = 30.0):
        self._hmac_key = hmac_signing_key
        self._challenge_ttl = challenge_ttl_sec
        
        # Реєстр публічних ключів (серійний номер -> public key object)
        self._device_registry: Dict[str, ec.EllipticCurvePublicKey] = {}
        
        # Чорний список серійних номерів (Revocation Blocklist)
        self._revocation_list: Set[str] = set()
        
        # Активні виклики: session_id -> (nonce, timestamp, client_ip)
        self._pending_challenges: Dict[str, Tuple[bytes, float, str]] = {}
        
        # Трекер географії та підключень для детекції копіювання: serial -> set(ips)
        self._device_ip_history: Dict[str, Set[str]] = {}

    def register_device(self, serial: str, public_key_pem: bytes) -> None:
        """Реєстрація фабричного публічного ключа оригінального пристрою."""
        pub_key = load_pem_public_key(public_key_pem)
        if isinstance(pub_key, ec.EllipticCurvePublicKey):
            self._device_registry[serial] = pub_key

    def issue_challenge(self, session_id: str, client_ip: str) -> bytes:
        """Генерація унікального криптографічного виклику CSPRNG."""
        nonce = secrets.token_bytes(32)
        self._pending_challenges[session_id] = (nonce, time.time(), client_ip)
        return nonce

    def authenticate_device(self, session_id: str, serial: str, 
                             signature_raw: bytes, client_ip: str) -> Tuple[bool, str, Optional[str]]:
        """Повна перевірка виклику, підпису, списку відкликання та аномалій."""
        challenge = self._pending_challenges.pop(session_id, None)
        if not challenge:
            return False, "ERR_SESSION_NOT_FOUND", None

        nonce, issued_at, initial_ip = challenge

        # 1. Перевірка актуальності виклику за часом
        if (time.time() - issued_at) > self._challenge_ttl:
            return False, "ERR_CHALLENGE_EXPIRED", None

        # 2. Перевірка знаходження в реєстрі відкликаних ключів
        if serial in self._revocation_list:
            return False, "ERR_DEVICE_REVOKED", None

        # 3. Пошук зареєстрованого публічного ключа
        pub_key = self._device_registry.get(serial)
        if not pub_key:
            return False, "ERR_UNREGISTERED_DEVICE", None

        # 4. Перевірка підпису ECDSA (NIST P-256 / SHA-256)
        try:
            pub_key.verify(signature_raw, nonce, ec.ECDSA(hashes.SHA256()))
        except Exception:
            return False, "ERR_INVALID_SIGNATURE", None

        # 5. Детекція клонування: аналіз одночасних географічних підключень
        ip_set = self._device_ip_history.setdefault(serial, set())
        ip_set.add(client_ip)
        if len(ip_set) > 8:
            # Зафіксовано підозрілу кількість унікальних IP-адрес для одного чипа
            self._revocation_list.add(serial)
            return False, "ERR_CLONE_COLLISION_DETECTED", None

        # 6. Формування авторизаційного токена доступу до сервісів
        expiry = int(time.time()) + 3600
        payload = f"{serial}:{expiry}:verified".encode("utf-8")
        token_mac = hmac.new(self._hmac_key, payload, "sha256").hexdigest()
        session_token = f"{payload.decode('utf-8')}.{token_mac}"

        return True, "AUTH_SUCCESS", session_token
