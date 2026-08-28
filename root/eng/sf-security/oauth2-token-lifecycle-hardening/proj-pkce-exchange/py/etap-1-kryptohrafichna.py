import os
import hashlib
import base64
import urllib.parse
from dataclasses import dataclass

def base64url_encode(data: bytes) -> str:
    """Кодування двійкових байтів у формат Base64URL без паддингу '='."""
    return base64.urlsafe_b64encode(data).decode('ascii').rstrip('=')

@dataclass
class OidcAuthorizationContext:
    verifier: str
    challenge: str
    state: str
    nonce: str

def create_oidc_context() -> OidcAuthorizationContext:
    """Генерація ентропії для verifier, state, nonce та обчислення challenge."""
    # 32 байти дають 43 символи Base64URL (повна відповідність RFC 7636)
    verifier = base64url_encode(os.urandom(32))
    state = base64url_encode(os.urandom(24))
    nonce = base64url_encode(os.urandom(24))

    # Обчислення незворотного SHA-256 хешу
    digest = hashlib.sha256(verifier.encode('ascii')).digest()
    challenge = base64url_encode(digest)

    return OidcAuthorizationContext(
        verifier=verifier,
        challenge=challenge,
        state=state,
        nonce=nonce
    )

def build_authorization_url(auth_endpoint: str, client_id: str,
                            redirect_uri: str, scope: str,
                            ctx: OidcAuthorizationContext) -> str:
    """Побудова повного URL запиту авторизації зі стандартними параметрами OIDC."""
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'state': ctx.state,
        'nonce': ctx.nonce,
        'code_challenge': ctx.challenge,
        'code_challenge_method': 'S256'
    }
    return f"{auth_endpoint}?{urllib.parse.urlencode(params)}"
