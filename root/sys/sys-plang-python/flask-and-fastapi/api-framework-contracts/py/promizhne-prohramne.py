class AuthenticationMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        token = environ.get("HTTP_X_SENSOR_TOKEN")
        if token != "valid-token":
            start_response("401 Unauthorized", [("Content-Type", "application/json")])
            return [b'{"error": "Unauthorized"}\n']
        return self.app(environ, start_response)
