import json
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler

class DeviceMetricsHandler(BaseHTTPRequestHandler):
    # Примусово вмикаємо версію HTTP/1.1 для коректної обробки Keep-Alive
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:
        if self.path == "/api/v1/status":
            response_data = {"status": "operational", "load": 0.42}
            payload = json.dumps(response_data).encode("utf-8")
            
            # Формування статусного рядка та обов'язкових заголовків
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            
            # Запис тіла відповіді
            self.wfile.write(payload)
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Запитуваний ресурс не існує")

    def do_POST(self) -> None:
        if self.path == "/api/v1/telemetry":
            content_length_str = self.headers.get("Content-Length")
            if not content_length_str or not content_length_str.isdigit():
                self.send_error(HTTPStatus.LENGTH_REQUIRED, "Обов'язковий заголовок Content-Length")
                return
            
            content_length = int(content_length_str)
            body_bytes = self.rfile.read(content_length)
            
            try:
                data = json.loads(body_bytes.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.send_error(HTTPStatus.BAD_REQUEST, "Некоректний JSON-документ")
                return
            
            ack_payload = json.dumps({"status": "recorded", "received_keys": list(data.keys())}).encode("utf-8")
            
            self.send_response(HTTPStatus.CREATED)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(ack_payload)))
            self.end_headers()
            self.wfile.write(ack_payload)
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Запитуваний ресурс не існує")
