import json
from urllib.parse import parse_qs

def router_wsgi_app(environ: dict, start_response) -> list[bytes]:
    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO", "/")

    if method == "GET" and path == "/api/status":
        query_params = parse_qs(environ.get("QUERY_STRING", ""))
        data = {"status": "ok", "query": query_params}
        payload = json.dumps(data).encode("utf-8")
        
        start_response("200 OK", [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(payload)))
        ])
        return [payload]

    if method == "POST" and path == "/api/data":
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0))
        except ValueError:
            content_length = 0
            
        if content_length > 0:
            body_bytes = environ["wsgi.input"].read(content_length)
            try:
                parsed_json = json.loads(body_bytes.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                start_response("400 Bad Request", [("Content-Type", "application/json")])
                return [b'{"error": "Invalid JSON format"}']
        else:
            parsed_json = {}

        response_obj = {"saved": True, "payload": parsed_json}
        payload = json.dumps(response_obj).encode("utf-8")
        
        start_response("201 Created", [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(payload)))
        ])
        return [payload]

    # Маршрут за замовчуванням
    start_response("404 Not Found", [("Content-Type", "application/json")])
    return [b'{"error": "Resource not found"}']
