import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Ініціалізація глобальних параметрів клієнта
CLIENT_ID = "my-saas-client-id"
CLIENT_SECRET = "super-secret-key-123"
ISSUER = "https://accounts.example.com"
DISCOVERY_URL = f"{ISSUER}/.well-known/openid-configuration"
REDIRECT_URI = "https://my-app.com/auth/callback"

# Локальні сховища стану (у продакшені — Redis із TTL)
pending_states = {} # state -> { nonce, code_verifier, created_at }
user_sessions = {}  # session_id -> { sub, email, name }

# Завантажуємо JWKS URI з discovery
jwks_mgr = JwksManager(jwks_uri=f"{ISSUER}/.well-known/jwks.json")

class OidcAuthServer(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        
        if path == "/auth/login":
            # 1. Створення параметрів та редирект
            ctx = create_authorization_url(
                authorization_endpoint=f"{ISSUER}/authorize",
                client_id=CLIENT_ID,
                redirect_uri=REDIRECT_URI
            )
            # Зберігаємо транзитний стан на 5 хвилин
            pending_states[ctx["state"]] = {
                "nonce": ctx["nonce"],
                "code_verifier": ctx["code_verifier"],
                "created_at": time.time()
            }
            self.send_response(302)
            self.send_header("Location", ctx["auth_url"])
            self.end_headers()
            
        elif path == "/auth/callback":
            # 2. Обробка повернення з провайдера
            state = query.get("state", [None])[0]
            code = query.get("code", [None])[0]
            error = query.get("error", [None])[0]
            
            if error:
                self.send_error(400, f"Помилка авторизації: {error}")
                return
                
            if not state or state not in pending_states:
                self.send_error(403, "Недійсний або протермінований параметр state (CSRF захист)")
                return
                
            saved_ctx = pending_states.pop(state)
            
            try:
                # 3. Обмін коду на токени
                token_res = exchange_code_for_tokens(
                    token_endpoint=f"{ISSUER}/token",
                    client_id=CLIENT_ID,
                    client_secret=CLIENT_SECRET,
                    code=code,
                    code_verifier=saved_ctx["code_verifier"],
                    redirect_uri=REDIRECT_URI
                )
                
                # 4. Валідація ID-токена
                claims = validate_id_token(
                    id_token_raw=token_res["id_token"],
                    expected_issuer=ISSUER,
                    expected_client_id=CLIENT_ID,
                    expected_nonce=saved_ctx["nonce"],
                    jwks_manager=jwks_mgr,
                    access_token_raw=token_res.get("access_token")
                )
                
                # 5. Отримання профілю
                profile = {}
                if "access_token" in token_res:
                    profile = fetch_userinfo(f"{ISSUER}/userinfo", token_res["access_token"])
                    
                # 6. Створення локальної сесії
                session_id = b64url_encode(os.urandom(32))
                user_sessions[session_id] = {
                    "sub": claims["sub"],
                    "email": profile.get("email", claims.get("email", "")),
                    "name": profile.get("name", claims.get("name", "")),
                    "id_token": token_res["id_token"]
                }
                
                self.send_response(302)
                self.send_header("Set-Cookie", f"session_id={session_id}; Path=/; HttpOnly; Secure; SameSite=Lax")
                self.send_header("Location", "/dashboard")
                self.end_headers()
                
            except Exception as e:
                self.send_error(401, f"Автентифікація не вдалася: {str(e)}")
