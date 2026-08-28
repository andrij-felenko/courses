import socket
import ssl
from http.server import BaseHTTPRequestHandler, HTTPServer


class MTLSHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Отримуємо розібраний сертифікат клієнта відкритого TLS-сокета
        client_cert = self.connection.getpeercert()
        subject = dict(x[0] for x in client_cert.get('subject', []))
        common_name = subject.get('commonName', 'Unknown')

        body = f"mTLS автентифікація успішна! Привіт, {common_name}\n".encode('utf-8')
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(port=8443):
    # Контекст для перевірки клієнтів (SERVER_AUTH для сервера, що приймає з'єднання)
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # Завантажуємо власний сертифікат сервера та його приватний ключ
    ctx.load_cert_chain(certfile="server.crt", keyfile="server.key")
    # Встановлюємо довірений Root CA для перевірки сертифікатів клієнтів
    ctx.load_verify_locations(cafile="ca.crt")
    # Вимагаємо обов'язкового надання валідного клієнтського сертифіката
    ctx.verify_mode = ssl.CERT_REQUIRED

    server = HTTPServer(('localhost', port), MTLSHandler)
    # Обгортаємо звичайний TCP сокет у захищений TLS шар
    server.socket = ctx.wrap_socket(server.socket, server_side=True)
    print(f"[*] mTLS HTTPS сервер слухає https://localhost:{port}")
    server.serve_forever()


if __name__ == '__main__':
    run_server()
