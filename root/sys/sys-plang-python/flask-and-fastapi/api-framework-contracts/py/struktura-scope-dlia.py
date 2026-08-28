{
    "type": "http",
    "asgi": {
        "version": "3.0",
        "spec_version": "2.3"
    },
    "http_version": "1.1",
    "method": "POST",
    "scheme": "http",
    "path": "/api/v1/telemetry",
    "raw_path": b"/api/v1/telemetry",
    "query_string": b"station_id=alpha&compress=gzip",
    "root_path": "",
    "headers": [
        [b"host", b"iot.factory.internal:8000"],
        [b"content-type", b"application/json"],
        [b"content-length", b"128"],
        [b"x-sensor-token", b"device-secret-key"]
    ],
    "client": ("192.168.1.50", 49152),
    "server": ("192.168.1.10", 8000),
    "state": {}
}
