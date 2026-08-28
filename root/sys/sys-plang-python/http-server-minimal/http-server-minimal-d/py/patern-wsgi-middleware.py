import time

class RequestTimingMiddleware:
    """Middleware для вимірювання часу генерації відповіді та додавання заголовка."""
    def __init__(self, application) -> None:
        self.application = application

    def __call__(self, environ: dict, start_response) -> list[bytes]:
        start_time = time.perf_counter()
        
        def timing_start_response(status, response_headers, exc_info=None):
            duration_ms = (time.perf_counter() - start_time) * 1000
            # Додаємо власний діагностичний заголовок
            response_headers.append(("X-Response-Time-Ms", f"{duration_ms:.2f}"))
            return start_response(status, response_headers, exc_info)

        return self.application(environ, timing_start_response)
