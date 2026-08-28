import json
import signal
import sys
import threading
import time
from http import HTTPStatus
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Any


class TelemetryDataStore:
    """Потокобезпечне сховище останніх показників датчиків та агрегованих метрик."""
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._start_time = time.time()
        self._total_requests_count = 0
        self._devices_telemetry: dict[str, dict[str, Any]] = {}

    def record_device_telemetry(self, device_id: str, payload: dict[str, Any]) -> None:
        with self._lock:
            self._total_requests_count += 1
            self._devices_telemetry[device_id] = {
                "metrics": payload,
                "updated_at": time.time(),
            }

    def get_system_snapshot(self) -> dict[str, Any]:
        with self._lock:
            self._total_requests_count += 1
            uptime = time.time() - self._start_time
            return {
                "status": "healthy",
                "uptime_seconds": round(uptime, 2),
                "total_http_requests": self._total_requests_count,
                "registered_devices_count": len(self._devices_telemetry),
                "devices": dict(self._devices_telemetry),
            }


# Глобальний екземпляр сховища стану
TELEMETRY_STORE = TelemetryDataStore()


class TelemetryMicroserverHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _write_json_response(self, status: HTTPStatus, data: dict[str, Any]) -> None:
        """Допоміжний метод формування та відправки JSON-відповіді з коректними заголовками."""
        try:
            payload = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        except TypeError as err:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Помилка серіалізації: {err}")
            return

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        if self.path == "/healthz":
            # Ендпоінт перевірки працездатності для Docker або Kubernetes Liveness Probe
            self._write_json_response(HTTPStatus.OK, {
                "service": "telemetry-node",
                "status": "healthy"
            })
        elif self.path in ("/metrics", "/api/v1/metrics"):
            # Ендпоінт моніторингу та агрегованого стану пристроїв
            snapshot = TELEMETRY_STORE.get_system_snapshot()
            self._write_json_response(HTTPStatus.OK, snapshot)
        else:
            self._write_json_response(HTTPStatus.NOT_FOUND, {
                "error": "Not Found",
                "message": f"Ендпоінт '{self.path}' не знайдено",
                "status_code": 404
            })

    def do_POST(self) -> None:
        if self.path in ("/telemetry", "/api/v1/telemetry"):
            content_length_header = self.headers.get("Content-Length")
            if not content_length_header or not content_length_header.isdigit():
                self._write_json_response(HTTPStatus.LENGTH_REQUIRED, {
                    "error": "Length Required",
                    "message": "Запит повинен містити числовий заголовок Content-Length"
                })
                return

            payload_length = int(content_length_header)
            # Захист від атак вичерпання пам'яті: обмежуємо корисне навантаження 64 кілобайтами
            max_allowed_payload = 65536
            if payload_length > max_allowed_payload:
                self._write_json_response(HTTPStatus.PAYLOAD_TOO_LARGE, {
                    "error": "Payload Too Large",
                    "message": f"Розмір тіла перевищує ліміт {max_allowed_payload} байтів"
                })
                return

            body_bytes = self.rfile.read(payload_length)
            try:
                parsed_payload = json.loads(body_bytes.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as parse_err:
                self._write_json_response(HTTPStatus.BAD_REQUEST, {
                    "error": "Bad Request",
                    "message": "Неможливо розібрати JSON-документ",
                    "details": str(parse_err)
                })
                return

            # Валідація схеми корисного навантаження
            device_id = parsed_payload.get("device_id")
            metrics_data = parsed_payload.get("metrics")

            if not device_id or not isinstance(device_id, str):
                self._write_json_response(HTTPStatus.UNPROCESSABLE_ENTITY, {
                    "error": "Unprocessable Entity",
                    "message": "Поле 'device_id' є обов'язковим непорожнім рядком"
                })
                return

            if not metrics_data or not isinstance(metrics_data, dict):
                self._write_json_response(HTTPStatus.UNPROCESSABLE_ENTITY, {
                    "error": "Unprocessable Entity",
                    "message": "Поле 'metrics' є обов'язковим об'єктом показників"
                })
                return

            # Атомарний запис у сховище
            TELEMETRY_STORE.record_device_telemetry(device_id, metrics_data)
            
            self._write_json_response(HTTPStatus.CREATED, {
                "status": "success",
                "device_id": device_id,
                "recorded_at": time.time()
            })
        else:
            self._write_json_response(HTTPStatus.NOT_FOUND, {
                "error": "Not Found",
                "message": f"Ендпоінт '{self.path}' не знайдено",
                "status_code": 404
            })

    def log_message(self, format_string: str, *args) -> None:
        """Перевизначення стандартного формату логування для чіткого моніторингу запитів."""
        client_ip, client_port = self.client_address
        log_entry = f"[{self.log_date_time_string()}] {client_ip}:{client_port} - {format_string % args}\n"
        sys.stdout.write(log_entry)
        sys.stdout.flush()


def run_standalone_telemetry_microserver(host: str = "0.0.0.0", port: int = 8080) -> None:
    """Запуск сервера у фоновому потоці з підтримкою Graceful Shutdown."""
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, TelemetryMicroserverHandler)
    
    # Запускаємо цикл прийому з'єднань у виділеному потоці
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=False)
    server_thread.start()
    print(f"Сервер телеметрії успішно запущено за адресою http://{host}:{port}")

    shutdown_trigger = threading.Event()

    def handle_termination_signal(signum: int, frame) -> None:
        print(f"\nОтримано системний сигнал ({signum}), ініціалізація коректної зупинки сервера...")
        shutdown_trigger.set()

    # Реєструємо перехоплення сигналів завершення
    signal.signal(signal.SIGINT, handle_termination_signal)
    signal.signal(signal.SIGTERM, handle_termination_signal)

    # Очікування сигналу завершення в головному потоці
    while not shutdown_trigger.is_set():
        shutdown_trigger.wait(timeout=0.5)

    print("Зупинка обробки нових TCP-з'єднань...")
    httpd.shutdown()
    server_thread.join()
    httpd.server_close()
    print("Сервер повністю зупинено. Мережеві сокети звільнено.")


if __name__ == "__main__":
    run_standalone_telemetry_microserver()
