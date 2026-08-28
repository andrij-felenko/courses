# 📋 Специфікація WSGI та ASGI: протокольні контракти серверів

Технічний довідник протокольних інтерфейсів WSGI (PEP 3333) та ASGI 3.0: структури словників оточення, сигнатури обробників, формати повідомлень HTTP/WebSocket, механізми зворотного тиску (backpressure) та обробка життєвого циклу додатків.

## Контракт WSGI (PEP 3333)

Синхронний веб-інтерфейс WSGI (англ. *Web Server Gateway Interface*) базується на концепції єдиного викликального об'єкта (функції або екземпляра класу з методом `__call__`), що приймає два позиційні аргументи:

```py
from collections.abc import Callable, Iterable

def application(
    environ: dict[str, object],
    start_response: Callable[
        [str, list[tuple[str, str]], tuple | None],
        Callable[[bytes], None]
    ]
) -> Iterable[bytes]:
    ...
```

### Життєвий цикл виконання WSGI-запиту

1. **Ініціалізація з'єднання**: Сервер (Gunicorn, uWSGI або Apache mod_wsgi) приймає вхідне TCP-з'єднання від клієнта через системний виклик `accept()`, зчитує байти HTTP-запиту, парсить початковий рядок та заголовки.
2. **Формування словника оточення**: Сервер створює словник `environ`, куди записує стандартні змінні оточення CGI, заголовки запиту клієнта та системні дескриптори вводу-виводу з префіксом `wsgi.`.
3. **Виклик обробника додатку**: Сервер викликає `application(environ, start_response)`. Додаток зчитує тіло запиту з бінарного потоку `environ["wsgi.input"]`.
4. **Реєстрація HTTP-заголовків**: Додаток викликає функцію `start_response(status, response_headers)`. Сервер буферизує статус-код та список заголовків, але ще не надсилає їх у сокет.
5. **Генерація та відправка тіла**: Додаток повертає ітерований об'єкт (список байтових рядків `[b"..."]` або генератор із викликами `yield`). Сервер ітерує цей об'єкт і відправляє порції байтів у мережевий сокет клієнта.
6. **Очищення ресурсів**: Якщо повернутий об'єкт має метод `close()`, сервер гарантовано викликає його у блоці `finally` після завершення передачі даних клієнту.

### Словник оточення `environ`

Словник `environ` передається за посиланням і містить системну інформацію про з'єднання:

| Ключ словника | Тип | Опис та приклад значення |
|---|---|---|
| `REQUEST_METHOD` | `str` | HTTP-метод запиту: `"GET"`, `"POST"`, `"PUT"`, `"DELETE"`. |
| `SCRIPT_NAME` | `str` | Початкова частина URL-шляху точки монтування додатку (може бути порожнім рядком `""`). |
| `PATH_INFO` | `str` | Залишкова частина URL-шляху для внутрішньої маршрутизації: `"/api/v1/sensors"`. |
| `QUERY_STRING` | `str` | Рядок параметрів URL після символу `?`: `"device_id=node_01&limit=100"`. |
| `CONTENT_TYPE` | `str` | Значення заголовка `Content-Type`: `"application/json; charset=utf-8"`. |
| `CONTENT_LENGTH` | `str` | Розмір тіла запиту в байтах у вигляді рядка: `"256"`. Порожній, якщо тіло відсутнє. |
| `SERVER_NAME` | `str` | Доменне ім'я або IP-адреса сервера: `"iot.factory.internal"`. |
| `SERVER_PORT` | `str` | TCP-порт прослуховування сервера: `"8080"`. |
| `SERVER_PROTOCOL` | `str` | Версія протоколу клієнта: `"HTTP/1.1"`. |
| `HTTP_*` | `str` | Усі заголовки запиту клієнта з префіксом `HTTP_` у верхньому регістрі (наприклад, `HTTP_AUTHORIZATION`). |
| `wsgi.version` | `tuple[int, int]` | Кортеж версії стандарту WSGI: `(1, 0)`. |
| `wsgi.url_scheme` | `str` | Схема підключення: `"http"` або `"https"`. |
| `wsgi.input` | `io.BufferedIOBase` | Потік вводу для читання тіла запиту через метод `read(size)`. |
| `wsgi.errors` | `io.TextIOBase` | Потік для запису системних помилок та журналів діагностики. |
| `wsgi.multithread` | `bool` | Прапорець: чи може екземпляр додатку викликатися паралельно іншим системним потоком. |
| `wsgi.multiprocess` | `bool` | Прапорець: чи запущено додаток у кількох незалежних процесах ОС. |
| `wsgi.run_once` | `bool` | Прапорець одноразового запуску процесу (типово для застарілого середовища CGI). |

### Функція зворотного виклику `start_response`

Функція `start_response` має сигнатуру:

```py
def start_response(
    status: str,
    response_headers: list[tuple[str, str]],
    exc_info: tuple | None = None
) -> Callable[[bytes], None]:
    ...
```

* `status`: текстовий статус HTTP з числовим кодом (наприклад, `"200 OK"`, `"422 Unprocessable Entity"`).
* `response_headers`: список 2-елементних кортежів `(назва_заголовка, значення)`. Назви заголовків мають бути рядками в кодуванні Latin-1 (ISO-8859-1).
* `exc_info`: системний кортеж винятку `sys.exc_info()`, який передається, якщо додаток змінює вже згенеровані заголовки у блоці перехоплення помилки.

Функція повертає застарілий викликач `write(body_data: bytes)`, використання якого не рекомендується сучасним стандартом PEP 3333 на користь повернення генератора.

### Проміжне програмне забезпечення у WSGI (Middleware)

WSGI дозволяє будувати ланцюжки обробників (Middleware), де кожен компонент є одночасно клієнтом для внутрішнього шару і сервером для зовнішнього:

```py
class AuthenticationMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        token = environ.get("HTTP_X_SENSOR_TOKEN")
        if token != "valid-token":
            start_response("401 Unauthorized", [("Content-Type", "application/json")])
            return [b'{"error": "Unauthorized"}\n']
        return self.app(environ, start_response)
```

### Обмеження потокового вводу та обробки помилок у WSGI

Специфікація WSGI має суттєві обмеження щодо обробки динамічних потоків даних:
1. **Потокове завантаження без фіксованого розміру (Chunked Transfer Encoding)**: WSGI вимагає наявності заголовка `CONTENT_LENGTH` для визначення розміру тіла. Якщо клієнт передає дані порціями без фіксованої довжини, сервер WSGI змушений повністю вичитати та збуферизувати весь запит у тимчасовий файл або пам'ять перед викликом додатку.
2. **Аварійний розрив з'єднання**: Якщо клієнт несподівано перериває TCP-сесію, сервер WSGI виявляє це лише під час спроби наступного запису в закритий сокет (системна помилка ядра `EPIPE` або виняток `BrokenPipeError`), що часто призводить до марного виконання важкої обчислювальної логіки.
3. **Потокобезпека та стан пам'яті**: Прапорець `environ["wsgi.multithread"]` інформує додаток про наявність конкурентних потоків. Оскільки об'єкти глобального простору імен є спільними для всіх потоків процесу CPython, фреймворки на зразок Flask змушені ізолювати контекст кожного запиту через локальне сховище потоків або контекстні змінні `ContextVar`.

## Контракт ASGI 3.0

Асинхронний стандарт ASGI (англ. *Asynchronous Server Gateway Interface*) розроблено для подолання обмежень синхронної блокувальної моделі. Додаток ASGI 3.0 є асинхронною корутиною:

```py
from collections.abc import Awaitable, Callable

async def application(
    scope: dict[str, object],
    receive: Callable[[], Awaitable[dict[str, object]]],
    send: Callable[[dict[str, object]], Awaitable[None]]
) -> None:
    ...
```

### Словник з'єднання `scope`

Словник `scope` містить контекст поточного з'єднання. Він створюється сервером один раз на початку сесії і не змінюється під час обміну повідомленнями.

#### Структура scope для протоколу HTTP (`scope["type"] == "http"`)

```py
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
```

Усі заголовки у списку `headers` передаються як кортежі сирих байтів `list[tuple[bytes, bytes]]` у нижньому регістрі. Це усуває накладні витрати на декодування рядків і запобігає спотворенню кодувань.

#### Структура scope для протоколу WebSocket (`scope["type"] == "websocket"`)

```py
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
```

### Протокол повідомлень HTTP

Спілкування між сервером (Uvicorn) та додатком (FastAPI) здійснюється передачею словників повідомлень через канали `receive()` та `send()`.

#### Вхідний потік повідомлень (Receive)

* **`http.request`**: передача порції тіла запиту від клієнта.
  * `type`: `"http.request"`
  * `body`: байти тіла запиту (`bytes`).
  * `more_body`: булеве значення. `True` вказує, що передача триває (streaming upload); `False` означає, що це останній фрагмент тіла.
* **`http.disconnect`**: надсилається сервером у канал `receive`, якщо клієнт несподівано розірвав TCP-з'єднання до завершення відповіді. Це дозволяє додатку негайно зупинити фонову обробку або скасувати асинхронну транзакцію в базі даних.

#### Вихідний потік повідомлень (Send)

1. **`http.response.start`**: відправка метаданих відповіді:
   * `type`: `"http.response.start"`
   * `status`: числовий код статусу HTTP (`int`, наприклад `200`, `400`, `422`, `500`).
   * `headers`: список пар байтів `list[tuple[bytes, bytes]]`.
2. **`http.response.body`**: відправка порції даних:
   * `type`: `"http.response.body"`
   * `body`: бінарний блок даних (`bytes`).
   * `more_body`: `True` для потокової передачі фрагментів (Chunked Transfer Encoding); `False` для фінального блоку.

### Механізм зворотного тиску (Backpressure)

Критичною перевагою ASGI над WSGI є вбудований асинхронний контроль швидкості передачі даних. Коли додаток викликає:

```py
await send({
    "type": "http.response.body",
    "body": chunk,
    "more_body": True
})
```

Оператор `await` блокує виконання корутини, якщо мережевий буфер сокета операційної системи (`SO_SNDBUF`) переповнений через повільне з'єднання клієнта. Сервер не зчитує нові порції даних із пам'яті чи диска, доки сокет не звільниться. Це унеможливлює виснаження пам'яті бекенду (OOM) під час передачі гігабайтних потоків телеметрії повільним польовим пристроям.

### Протокол повідомлень WebSocket

| Подія повідомлення | Напрямок | Обов'язкові поля | Призначення |
|---|---|---|---|
| `websocket.connect` | Сервер → Додаток | `type: "websocket.connect"` | Запит клієнта на встановлення двонаправленого з'єднання. |
| `websocket.accept` | Додаток → Сервер | `subprotocol: str \| None`, `headers: list` | Підтвердження успішного рукостискання (Handshake). |
| `websocket.receive` | Сервер → Додаток | `bytes: bytes \| None`, `text: str \| None` | Вхідний бінарний чи текстовий фрейм від датчика. |
| `websocket.send` | Додаток → Сервер | `bytes: bytes \| None`, `text: str \| None` | Відправка команди чи пакета телеметрії клієнту. |
| `websocket.close` | Додаток → Сервер | `code: int`, `reason: str` | Закриття сесії з кодом протоколу (наприклад, 1000 — штатне закриття). |
| `websocket.disconnect` | Сервер → Додаток | `code: int` | Сповіщення про втрату зв'язку з клієнтом. |

### Події життєвого циклу (Lifespan Protocol)

Протокол Lifespan дозволяє додатку виконати асинхронну ініціалізацію спільних системних ресурсів (пулів підключень до PostgreSQL через `asyncpg`, клієнтів Redis, брокерів MQTT) до відкриття мережевого порту сервером:

```py
async def lifespan_handler(scope, receive, send):
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                try:
                    # Асинхронний старт системних пулів
                    await database_engine.connect()
                    await send({"type": "lifespan.startup.complete"})
                except Exception as exc:
                    await send({"type": "lifespan.startup.failed", "message": str(exc)})
                    return
            elif message["type"] == "lifespan.shutdown":
                # Гарантоване закриття з'єднань і збереження буферів
                await database_engine.disconnect()
                await send({"type": "lifespan.shutdown.complete"})
                return
```

### Проміжне програмне забезпечення у ASGI (Middleware)

У середовищі ASGI проміжний шар реалізується як обгортка над корутиною:

```py
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
```

## Порівняння протокольних характеристик

| Характеристика | WSGI (PEP 3333) | ASGI 3.0 |
|---|---|---|
| **Тип виклику** | Синхронна функція | Асинхронна корутина (`async def`) |
| **Парадигма I/O** | Блокувальний потік або процес | Неблокувальний цикл подій (`event loop`) |
| **Кодування заголовків** | Рядки `str` (Latin-1 / ISO-8859-1) | Сирі байти `bytes` (UTF-8) |
| **Підтримка WebSockets** | Відсутня (вимагає сторонніх хаків) | Нативна на рівні специфікації |
| **Керування станом** | Локальні змінні потоку (`threading.local`) | Словник контексту `scope["state"]` |
| **Зворотний тиск (Backpressure)** | Відсутній (залежить від буферів ОС) | Вбудований асинхронний через `await send()` |
| **Керування життєвим циклом** | Не стандартизовано | Протокол Lifespan (`startup`/`shutdown`) |
| **Сервери реалізації** | Gunicorn (sync), uWSGI, Waitress | Uvicorn (uvloop), Hypercorn, Granian |
