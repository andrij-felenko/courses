import urllib.request
import ssl
import requests


def mtls_urllib_request(url="https://localhost:8443/"):
    # Створюємо контекст клієнта та завантажуємо кореневий CA для перевірки сервера
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile="ca.crt")
    # Завантажуємо клієнтський сертифікат і приватний ключ для mTLS
    ctx.load_cert_chain(certfile="client.crt", keyfile="client.key")
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED

    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=ctx) as response:
        print(f"[urllib] Статус: {response.status}")
        print("[urllib] Тіло відповіді:", response.read().decode('utf-8'))


def mtls_requests_client(url="https://localhost:8443/"):
    # Бібліотека requests приймає пару (cert, key) для клієнтської автентифікації
    resp = requests.get(
        url,
        verify="ca.crt",
        cert=("client.crt", "client.key")
    )
    print(f"[requests] Статус: {resp.status_code}")
    print(f"[requests] Тіло: {resp.text}")


if __name__ == '__main__':
    mtls_urllib_request()
    mtls_requests_client()
