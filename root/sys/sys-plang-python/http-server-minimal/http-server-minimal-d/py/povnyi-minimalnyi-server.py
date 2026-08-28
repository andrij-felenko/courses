import json
import socket

def run_minimal_socket_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Вимикаємо алгоритм Нейгла для мінімізації затримок відправки дрібних відповідей
    server_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    
    server_sock.bind((host, port))
    server_sock.listen(128)
    
    try:
        while True:
            client_sock, client_addr = server_sock.accept()
            with client_sock:
                try:
                    header_bytes, rest_body = read_http_headers(client_sock)
                    method, path, version, headers = parse_http_request(header_bytes)
                    
                    content_length = int(headers.get("content-length", 0))
                    body = read_http_body(client_sock, rest_body, content_length) if content_length > 0 else b""
                    
                    # Маршрутизація
                    if method == "GET" and path == "/healthz":
                        payload = b'{"status": "healthy"}'
                        send_http_response(client_sock, 200, "OK",
                                           {"content-type": "application/json; charset=utf-8"}, payload)
                    elif method == "POST" and path == "/echo":
                        send_http_response(client_sock, 200, "OK",
                                           {"content-type": "application/octet-stream"}, body)
                    else:
                        payload = json.dumps({"error": "Resource not found", "path": path}).encode("utf-8")
                        send_http_response(client_sock, 404, "Not Found",
                                           {"content-type": "application/json; charset=utf-8"}, payload)
                except Exception as exc:
                    err_payload = json.dumps({"error": str(exc)}).encode("utf-8")
                    send_http_response(client_sock, 400, "Bad Request",
                                       {"content-type": "application/json; charset=utf-8"}, err_payload)
    finally:
        server_sock.close()
