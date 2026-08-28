def handle_backchannel_logout(
    logout_token_raw: str,
    expected_issuer: str,
    expected_client_id: str,
    jwks_manager: JwksManager
) -> str:
    """Обробка Logout Token та повернення sub користувача для інвалідації сесій."""
    parts = logout_token_raw.split('.')
    if len(parts) != 3:
        raise ValueError("Некоректний формат Logout Token")
        
    header = json.loads(JwksManager._b64url_decode(parts[0]).decode('utf-8'))
    public_key = jwks_manager.get_key(header["kid"])
    
    # Верифікація підпису
    signed_data = f"{parts[0]}.{parts[1]}".encode('ascii')
    signature = JwksManager._b64url_decode(parts[2])
    public_key.verify(signature, signed_data, padding.PKCS1v15(), hashes.SHA256())
    
    payload = json.loads(JwksManager._b64url_decode(parts[1]).decode('utf-8'))
    
    # Перевірка обов'язкових інваріантів Logout Token
    if payload.get("iss") != expected_issuer:
        raise ValueError("Невідповідність iss у Logout Token")
        
    aud = payload.get("aud")
    if aud != expected_client_id and (isinstance(aud, list) and expected_client_id not in aud):
        raise ValueError("Невідповідність aud у Logout Token")
        
    if "nonce" in payload:
        raise ValueError("Logout Token містить заборонене поле nonce!")
        
    events = payload.get("events", {})
    if "http://schemas.openid.net/event/backchannel-logout" not in events:
        raise ValueError("Відсутній обов'язковий маркер події backchannel-logout")
        
    sub = payload.get("sub")
    if not sub and not payload.get("sid"):
        raise ValueError("Logout Token зобов'язаний містити sub або sid")
        
    return sub
