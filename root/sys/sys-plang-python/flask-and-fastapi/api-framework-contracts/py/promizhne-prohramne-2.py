class TelemetryTimingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        import time
        start_time = time.perf_counter()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                duration_ms = (time.perf_counter() - start_time) * 1000.0
                headers = list(message.get("headers", []))
                headers.append((b"x-process-time-ms", f"{duration_ms:.2f}".encode("ascii")))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_wrapper)
