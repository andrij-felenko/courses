# Внутрішня диспетчеризація в BaseHTTPRequestHandler
self.command = method  # Наприклад, "GET" або "POST"
self.path = url_path   # Наприклад, "/metrics?format=json"

mname = "do_" + self.command
if not hasattr(self, mname):
    self.send_error(
        HTTPStatus.NOT_IMPLEMENTED,
        f"Unsupported method ({self.command})"
    )
    return
method_handler = getattr(self, mname)
method_handler()  # Виклик призначеного користувацького методу do_GET() / do_POST()
