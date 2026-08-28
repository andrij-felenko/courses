import ssl
import urllib.request
import requests
from requests.adapters import HTTPAdapter


def make_custom_ssl_context(ca_bundle_path: str, client_cert_path: str = None, client_key_path: str = None) -> ssl.SSLContext:
    """Створює захищений клієнтський SSL-контекст за сучасними стандартами безпеки."""
    # Створюємо базовий контекст із протоколом TLS для клієнта
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

    # 1. Завантажуємо власний довірений CA бандл замість системного дефолту
    context.load_verify_locations(cafile=ca_bundle_path)

    # 2. Суворо вимагаємо перевірки сертифіката сервера та його імені
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = True

    # 3. Обмежуємо версії протоколу сучасними стандартами TLS 1.2 та 1.3
    context.minimum_version = ssl.TLSVersion.TLSv1_2

    # 4. Якщо надано клієнтські ключі — завантажуємо їх для mTLS
    if client_cert_path and client_key_path:
        context.load_cert_chain(certfile=client_cert_path, keyfile=client_key_path)

    return context


def fetch_with_urllib():
    ctx = make_custom_ssl_context("corp-ca.pem", "client.crt", "client.key")
    req = urllib.request.Request("https://api.internal.corp/v1/status")
    with urllib.request.urlopen(req, context=ctx, timeout=5.0) as resp:
        print(f"HTTP статус: {resp.status}, Відповідь: {resp.read().decode('utf-8')}")


def fetch_with_requests():
    """Використання кастомного CA та клієнтського сертифіката mTLS у бібліотеці requests."""
    session = requests.Session()
    # verify вказує шлях до CA бандла, cert — пару (клієнтський сертифікат, приватний ключ)
    resp = session.get(
        "https://api.internal.corp/v1/status",
        verify="corp-ca.pem",
        cert=("client.crt", "client.key"),
        timeout=5.0
    )
    print(f"Requests статус: {resp.status_code}, Тіло: {resp.text}")
