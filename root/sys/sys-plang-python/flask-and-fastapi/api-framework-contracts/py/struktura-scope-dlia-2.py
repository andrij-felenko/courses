{
    "type": "websocket",
    "asgi": {"version": "3.0", "spec_version": "2.3"},
    "http_version": "1.1",
    "scheme": "ws",
    "path": "/ws/v1/live-feed",
    "raw_path": b"/ws/v1/live-feed",
    "query_string": b"device_id=node_42",
    "root_path": "",
    "headers": [
        [b"host", b"iot.factory.internal:8000"],
        [b"upgrade", b"websocket"],
        [b"connection", b"Upgrade"],
        [b"sec-websocket-key", b"dGhlIHNhbXBsZSBub25jZQ=="],
        [b"sec-websocket-version", b"13"]
    ],
    "client": ("192.168.1.50", 49154),
    "server": ("192.168.1.10", 8000),
    "subprotocols": ["sensor-binary-v2"]
}
