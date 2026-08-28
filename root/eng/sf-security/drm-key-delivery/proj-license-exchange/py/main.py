"""
License Proxy Server: Перевірка JWT та маршрутизація запиту до KMS.
"""
from aiohttp import web
import jwt
import hmac
import hashlib
import os

JWT_SECRET = os.environ.get("DRM_JWT_SECRET", "super-secret-key-123")
KMS_INTERNAL_URL = "http://kms.internal.service/api/v1/license"

async def handle_license_request(request: web.Request) -> web.Response:
    # 1. Валідація заголовка авторизації
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return web.Response(status=401, text="Відсутній або некоректний токен авторизації")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        has_active_subscription = payload.get("active_sub", False)
        max_allowed_resolution = payload.get("max_res", "1080p")
    except jwt.PyJWTError as e:
        return web.Response(status=403, text=f"Помилка перевірки токена: {str(e)}")

    if not has_active_subscription:
        return web.Response(status=402, text="Підписку користувача вичерпано")

    # 2. Отримання двійкового License Challenge від браузера
    challenge_bytes = await request.read()
    if not challenge_bytes:
        return web.Response(status=400, text="Порожнє тіло челенджу")

    # 3. Передача челенджу в ядро DRM KMS із додаванням бізнес-політик
    # Внутрішній KMS перевіряє сертифікат пристрою та загортає Content Key
    kms_headers = {
        "X-User-ID": str(user_id),
        "X-Max-Resolution": max_allowed_resolution,
        "X-Require-HDCP": "true" if max_allowed_resolution == "4k" else "false",
        "Content-Type": "application/octet-stream"
    }

    # Емуляція звернення до захищеного криптомодуля KMS
    # У бойовій системі тут викликається RPC/gRPC до Widevine KMS / PlayReady Server
    license_response_bytes = generate_mock_license_response(challenge_bytes, max_allowed_resolution)

    return web.Response(
        body=license_response_bytes,
        status=200,
        content_type="application/octet-stream"
    )

def generate_mock_license_response(challenge: bytes, max_res: str) -> bytes:
    # Структура відповіді: [4 байти Magic: 'LICR'] [1 байт Status] [Payload...]
    header = b"LICR\x00"
    policy_flag = b"\x02" if max_res == "4k" else b"\x01"
    # Додаємо псевдовипадковий загорнутий блок ключа
    wrapped_key = hashlib.sha256(challenge).digest()[:24]
    return header + policy_flag + wrapped_key

app = web.Application()
app.router.add_post("/api/drm/license", handle_license_request)

if __name__ == "__main__":
    web.run_app(app, port=8080)
