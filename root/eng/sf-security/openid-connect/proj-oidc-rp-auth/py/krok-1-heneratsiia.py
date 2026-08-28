import os
import base64
import hashlib
import urllib.parse

def b64url_encode(data: bytes) -> str:
    """Кодування сирих байтів у безпечний рядок Base64URL без знаків '='."""
    return base64.urlsafe_b64encode(data).decode('ascii').rstrip('=')

def generate_pkce_pair() -> tuple[str, str]:
    """Генерація випадкового code_verifier та розрахунок code_challenge (S256)."""
    verifier_bytes = os.urandom(32) # 256 біт ентропії
    code_verifier = b64url_encode(verifier_bytes)
    
    digest = hashlib.sha256(code_verifier.encode('ascii')).digest()
    code_challenge = b64url_encode(digest)
    return code_verifier, code_challenge

def create_authorization_url(
    authorization_endpoint: str,
    client_id: str,
    redirect_uri: str,
    scope: str = "openid profile email"
) -> dict:
    state = b64url_encode(os.urandom(24))
    nonce = b64url_encode(os.urandom(24))
    code_verifier, code_challenge = generate_pkce_pair()
    
    params = {
        "client_id": client_id,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": redirect_uri,
        "state": state,
        "nonce": nonce,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "response_mode": "query"
    }
    
    query_string = urllib.parse.urlencode(params)
    auth_url = f"{authorization_endpoint}?{query_string}"
    
    return {
        "auth_url": auth_url,
        "state": state,
        "nonce": nonce,
        "code_verifier": code_verifier,
    }
