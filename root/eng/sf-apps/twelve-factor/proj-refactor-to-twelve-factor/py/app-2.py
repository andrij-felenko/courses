# app.py (фрагмент) — порт із конфігу + штатне завершення за SIGTERM.
import signal
from wsgiref.simple_server import make_server
from config import config

def build_app():
    ...  # той самий Flask/WSGI-застосунок

def main():
    app = build_app()
    # Порт — із середовища (крок 1), а не число в коді.
    httpd = make_server("0.0.0.0", config.PORT, app)

    def on_term(signum, frame):
        # Прийшов SIGTERM: перестати брати нові з'єднання...
        httpd.shutdown()          # ← перестаємо приймати, дообслуговуємо поточні
        # ...тут місце дозакрити те, що почали:
        #    доробити запити в роботі, повернути завдання в чергу,
        #    відпустити з'єднання до бази й кешу — і лише тоді вийти.

    signal.signal(signal.SIGTERM, on_term)   # ← перехоплюємо ввічливе «спинись»
    signal.signal(signal.SIGINT, on_term)    # той самий обряд і на Ctrl-C
    httpd.serve_forever()

if __name__ == "__main__":
    main()
