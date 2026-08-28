import hmac

def validate_callback_state(param_state: str, session_state: str) -> bool:
    """Порівняння отриманого state зі збереженим сталим часом."""
    if not param_state or not session_state:
        return False
    return hmac.compare_digest(param_state, session_state)

def format_token_exchange_payload(code: str, verifier: str,
                                  redirect_uri: str, client_id: str,
                                  client_secret: str = None) -> dict:
    """Підготовка тіла POST-запиту на ендпоінт /token."""
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'code_verifier': verifier
    }
    if client_secret:
        payload['client_secret'] = client_secret
    return payload
