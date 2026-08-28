from wsgiref.validate import validator
from wsgiref.simple_server import make_server


def my_app(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
    return [b"Valid WSGI response"]


# Обгортання додатку валідатором для перевірки сумісності
strict_app = validator(my_app)

if __name__ == "__main__":
    with make_server("127.0.0.1", 8080, strict_app) as httpd:
        httpd.serve_forever()
