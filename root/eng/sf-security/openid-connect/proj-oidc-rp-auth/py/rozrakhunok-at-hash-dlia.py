from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import hmac

def validate_id_token(
    id_token_raw: str,
    expected_issuer: str,
    expected_client_id: str,
    expected_nonce: str,
    jwks_manager: JwksManager,
    access_token_raw: str | None = None,
    clock_skew_sec: int = 60
) -> dict:
    parts = id_token_raw.split('.')
    if len(parts) != 3:
        raise ValueError("Некоректний формат JWT: очікується рівно три частини")
        
    header_b64, payload_b64, sig_b64 = parts
    
    # 1. Розбір та перевірка заголовка
    header_bytes = JwksManager._b64url_decode(header_b64)
    header = json.loads(header_bytes.decode('utf-8'))
    
    alg = header.get("alg")
    if alg != "RS256":
        raise ValueError(f"Недозволений алгоритм підпису: {alg}. Очікується RS256")
        
    kid = header.get("kid")
    if not kid:
        raise ValueError("У заголовку JWT відсутнє обов'язкове поле kid")
        
    # 2. Отримання відкритого ключа та перевірка підпису
    public_key = jwks_manager.get_key(kid)
    signed_payload = f"{header_b64}.{payload_b64}".encode('ascii')
    signature = JwksManager._b64url_decode(sig_b64)
    
    try:
        public_key.verify(
            signature,
            signed_payload,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
    except Exception as exc:
        raise ValueError("Цифровий підпис ID-токена не пройшов верифікацію!") from exc
        
    # 3. Розбір навантаження (claims)
    payload_bytes = JwksManager._b64url_decode(payload_b64)
    payload = json.loads(payload_bytes.decode('utf-8'))
    now = time.time()
    
    # 4. Перевірка видавця (iss)
    if payload.get("iss") != expected_issuer:
        raise ValueError(f"Невідповідність iss: очікувалось {expected_issuer}, отримано {payload.get('iss')}")
        
    # 5. Перевірка аудиторії (aud)
    aud = payload.get("aud")
    if isinstance(aud, str):
        if aud != expected_client_id:
            raise ValueError(f"Невідповідність aud: {aud} != {expected_client_id}")
    elif isinstance(aud, list):
        if expected_client_id not in aud:
            raise ValueError(f"client_id {expected_client_id} відсутній у списку aud: {aud}")
        if len(aud) > 1 and payload.get("azp") != expected_client_id:
            raise ValueError("Для множинного aud значення azp має дорівнювати client_id")
    else:
        raise ValueError("Відсутнє або некоректне поле aud")
        
    # 6. Перевірка часових міток (exp, iat)
    exp = payload.get("exp")
    if not exp or (exp + clock_skew_sec) < now:
        raise ValueError("Термін дії ID-токена сплив (exp)")
        
    iat = payload.get("iat")
    if iat and (iat - clock_skew_sec) > now:
        raise ValueError("Токен випущено в майбутньому (iat)")
        
    # 7. Звірка Nonce
    if payload.get("nonce") != expected_nonce:
        raise ValueError("Порушення nonce: токен не відповідає початковому запиту входу")
        
    # 8. Звірка at_hash
    if access_token_raw and "at_hash" in payload:
        digest = hashlib.sha256(access_token_raw.encode('ascii')).digest()
        half_len = len(digest) // 2
        expected_at_hash = b64url_encode(digest[:half_len])
        if not hmac.compare_digest(payload["at_hash"], expected_at_hash):
            raise ValueError("Невідповідність at_hash: access_token підмінено!")
            
    return payload
