# Найпростіший HTTP-сервер

<preknowlist>
- [Модуль socket і TCP-з'єднання](root:sys-plang-python/socket-module) — низькорівневі системні виклики socket, bind, listen, accept та передача байтових потоків.
- [bytes, bytearray і memoryview](root:sys-plang-python/bytes-and-memoryview) — представлення сирих байтів, буферизація та маніпуляції з бінарними даними без копіювання.
- [Кодування, UTF-8 і помилки декодування](root:sys-plang-python/encodings-and-utf8) — перетворення між str та bytes за стандартами Unicode, UTF-8 та Latin-1.
- [Потоки в threading](root:sys-plang-python/threading-basics) — паралельне виконання задач у потоках ОС, поділ пам'яті та синхронізація через замки.
- [Протокол HTTP](root:com-protocol/http) — структура запитів і відповідей HTTP/1.1, стартовий рядок, заголовки та семантика методів.
</preknowlist>

Коли мікроконтролерний шлюз надсилає пакет телеметрії розміром 128 байтів через команду `curl -X POST http://127.0.0.1:8080/telemetry -d '{"temp": 23.5}'`, операційна система отримує не готовий об'єкт повідомлення, а неперервний двійковий потік TCP. Якщо сервер викликає `sock.recv(4096)` лише один раз і очікує отримати повний HTTP-запит, фрагментація пакетів на рівні IP або затримка передачі заголовків розриває корисне навантаження: сервер зчитує лише стартовий рядок, парсер виходить із ладу, а клієнт зависає в очікуванні відповіді до настання таймауту. Робота вебсервера починається з розмежування повідомлень у потоці байтів і перетворення сирого дескриптора сокета на структуровані запити та відповіді.

## 1. Низькорівневий сокетний HTTP-сервер на базі модуля socket

Мережевий стек операційної системи на транспортному рівні TCP надає прикладній програмі абстракцію надійного повнодуплексного байтового потоку (Byte Stream). На відміну від протоколу UDP, де одиницею передачі є дискретна датаграма із фіксованими межами, TCP нічого не знає про логічні межі вищих протоколів. Дані, записані клієнтом за допомогою трьох послідовних викликів `send()`, можуть бути об'єднані стеком ядра в один TCP-сегмент або, навпаки, розбиті на десятки дрібних пакетів через обмеження максимального розміру корисного навантаження (Maximum Segment Size, MSS).

Протокол HTTP/1.1 вирішує проблему структурування за допомогою текстового кадрування. Кожне повідомлення клієнта складається з трьох обов'язкових секцій:
1. **Стартовий рядок запиту (Request Line):** містить назву методу, шлях до ресурсу та версію протоколу, відокремлені одинарними пробілами та завершені послідовністю символів повернення каретки й переведення рядка `\r\n` (CRLF, коди `0x0D 0x0A`).
2. **Блок заголовків (Headers Block):** набір текстових рядків формату `Назва: Значення\r\n`, що визначають метадані запиту (хост, тип корисного навантаження, параметри автентифікації).
3. **Маркер кінця заголовків:** порожній рядок `\r\n`. Повна послідовність на стику заголовків і тіла утворює чотирибайтовий двійковий роздільник `\r\n\r\n` (`0x0D 0x0A 0x0D 0x0A`).
4. **Тіло повідомлення (Message Body):** довільний масив двійкових або текстових даних, довжина якого або прямо задається числовим заголовком `Content-Length`, або транслюється динамічними порціями за наявності заголовка `Transfer-Encoding: chunked`.

![Життєвий цикл сокетного HTTP-сервера: від TCP-байтів до відповіді](/root/sys/sys-plang-python/http-server-minimal/img/http-socket-lifecycle.svg)
*Життєвий цикл сокетного HTTP-сервера: прийом з'єднання через accept(), накопичення буфера до появи CRLF CRLF, вичитування тіла фіксованої довжини та відправка відповіді.*

### Механіка буферизації та виявлення роздільника заголовків

Оскільки одиничний системний виклик `recv(chunk_size)` повертає довільну кількість байтів від 1 до `chunk_size` (залежно від того, скільки даних встиг передати мережевий адаптер у буфер сокета ядра `SO_RCVBUF`), сервер повинен організувати цикл накопичення. Якщо сервер наївно очікує, що всі заголовки надійдуть в одному першому виклику `recv()`, повільне з'єднання або передача заголовків частинами призведе до спроби розібрати неповний рядок і аварійного розриву зв'язку.

Правильний алгоритм полягає у зчитуванні байтів у змінний масив `bytearray` до моменту, поки метод пошуку підрядка `buffer.find(b"\r\n\r\n")` не поверне невід'ємний індекс:

```python
import socket

def read_http_headers(client_sock: socket.socket) -> tuple[bytes, bytes]:
    """Вичитує двійкові дані із сокета до виявлення роздільника \\r\\n\\r\\n.
    
    Повертає кортеж із двох елементів:
      1. header_bytes — сирий двійковий блок стартового рядка та заголовків;
      2. rest_body — залишок байтів, прочитаних у буфер понад заголовки.
    """
    buffer = bytearray()
    delimiter = b"\r\n\r\n"
    max_header_size = 65536  # Захист від вичерпання пам'яті завеликими заголовками
    
    while True:
        pos = buffer.find(delimiter)
        if pos != -1:
            header_bytes = bytes(buffer[:pos])
            rest_body = bytes(buffer[pos + len(delimiter):])
            return header_bytes, rest_body
        
        if len(buffer) >= max_header_size:
            raise ValueError("Розмір заголовків HTTP перевищує дозволений ліміт 64 КБ")
            
        chunk = client_sock.recv(4096)
        if not chunk:
            # Якщо клієнт закрив сокет (EOF), не передавши CRLF CRLF, запит некоректний
            raise ConnectionResetError("Клієнт розірвав з'єднання до завершення передачі заголовків")
        buffer.extend(chunk)
```

Зверніть увагу на збереження залишку `rest_body`. Якщо розмір вхідного TCP-пакета перевищував сумарний розмір заголовків, виклик `recv(4096)` разом із заголовками вичитує перші байти корисного навантаження (тіла POST-запиту). Втрата цього залишку зруйнує цілісність вхідного файлу чи JSON-документа.

### Синтаксичний розбір стартового рядка та заголовків

Отриманий двійковий блок заголовків декодується в текст за стандартом Latin-1 (ISO-8859-1). Цей вибір кодування гарантує, що жоден байт у діапазоні `0x00`–`0xFF` не викличе винятку `UnicodeDecodeError`, оскільки кодування Latin-1 прямо відображає кожен байт у відповідний код-пойнт Unicode.

Перший рядок розбивається на три обов'язкові компоненти:
- `method`: текстова назва операції (`GET`, `POST`, `PUT`, `DELETE`, `HEAD`, `OPTIONS`);
- `path`: відносний уніфікований ідентифікатор ресурсу (URI) разом із необов'язковим рядком параметрів запиту;
- `version`: ідентифікатор версії протоколу, зазвичай `HTTP/1.1` або `HTTP/1.0`.

Усі подальші рядки містять заголовки. Згідно зі специфікацією RFC 7230, назви заголовків нечутливі до регістру символів (`Content-Type`, `content-type` та `CONTENT-TYPE` позначають один і той самий параметр). Тому сервер під час розбору обов'язково переводить назви ключів у нижній регістр:

```python
def parse_http_request(header_bytes: bytes) -> tuple[str, str, str, dict[str, str]]:
    text = header_bytes.decode("iso-8859-1")
    lines = text.split("\r\n")
    if not lines or not lines[0]:
        raise ValueError("Порожній HTTP-запит")
    
    # Синтаксичний аналіз стартового рядка
    request_line = lines[0].strip()
    parts = request_line.split(" ")
    if len(parts) != 3:
        raise ValueError(f"Некоректний формат стартового рядка: '{request_line}'")
    
    method, path, version = parts
    
    # Синтаксичний аналіз заголовків
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if not line:
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        headers[key.strip().lower()] = value.strip()
        
    return method, path, version, headers
```

### Детерміноване вичитування тіла запиту

Якщо клієнт надіслав запит із корисним навантаженням (типово для методів `POST`, `PUT`, `PATCH`), він передає заголовок `content-length`, що містить точну кількість байтів тіла у вигляді десяткового числа. Читання тіла полягає у витягуванні рівно вказаної кількості байтів:

```python
def read_http_body(client_sock: socket.socket, rest_body: bytes, content_length: int) -> bytes:
    if len(rest_body) >= content_length:
        return rest_body[:content_length]
    
    body = bytearray(rest_body)
    bytes_remaining = content_length - len(body)
    
    while bytes_remaining > 0:
        chunk = client_sock.recv(min(4096, bytes_remaining))
        if not chunk:
            raise ConnectionResetError("Передчасний обрив TCP-потоку під час читання тіла запиту")
        body.extend(chunk)
        bytes_remaining -= len(chunk)
        
    return bytes(body)
```

Спроба прочитати тіло викликом `client_sock.recv(4096)` без контролю лічильника `bytes_remaining` або виклик `client_sock.recv()` у нескінченному циклі до отримання порожнього рядка призведе до мертвого блокування (Deadlock). Клієнт, передавши всі байти свого JSON-пакета, тримає TCP-з'єднання відкритим і чекає на відповідь, а сервер чекає на EOF від клієнта, якого ніколи не надійде.

### Формування та відправка коректної HTTP-відповіді

Формування відповіді підпорядковується суворим інваріантам:
1. Стартовий рядок статусу: версія протоколу, тризначний десятковий код та нормативна фраза опису (`HTTP/1.1 200 OK\r\n` або `HTTP/1.1 404 Not Found\r\n`).
2. Заголовок `Content-Length`: обов'язковий заголовок, що вказує клієнту розмір тіла відповіді в байтах. Якщо його пропустити в режимі HTTP/1.1, клієнт не знатиме, де закінчується документ, і не зможе розірвати або повторно використати з'єднання.
3. Заголовок `Content-Type`: визначає MIME-тип та кодування даних (`application/json; charset=utf-8` або `text/html; charset=utf-8`).
4. Заголовок `Connection`: вказує політику керування з'єднанням. Значення `close` сповіщає клієнта, що після передачі цієї відповіді сервер негайно закриє TCP-дескриптор.
5. Відправка через `sendall()`: стандартний метод `socket.send()` не гарантує передачу всього буфера за один виклик ядра. Метод `sendall()` автоматично повторює системний виклик у циклі, доки всі байти не потраплять у вихідний буфер операційної системи `SO_SNDBUF`.

```python
def send_http_response(client_sock: socket.socket, status_code: int, reason: str,
                       headers: dict[str, str], body: bytes) -> None:
    headers["content-length"] = str(len(body))
    headers["connection"] = "close"
    
    response_lines = [f"HTTP/1.1 {status_code} {reason}"]
    for key, value in headers.items():
        response_lines.append(f"{key}: {value}")
    response_lines.append("")
    response_lines.append("")
    
    header_block = "\r\n".join(response_lines).encode("iso-8859-1")
    client_sock.sendall(header_block + body)
```

### Повний мінімальний сервер на чистих сокетах

Збираючи ці модулі в єдиний виконуваний каркас із конфігурацією сокета (`SO_REUSEADDR` для можливості миттєвого перезапуску на тому самому порту без очікування стану ядра `TIME_WAIT`), отримуємо повноцінний автономний сервер:

```python
import json
import socket

def run_minimal_socket_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Вимикаємо алгоритм Нейгла для мінімізації затримок відправки дрібних відповідей
    server_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    
    server_sock.bind((host, port))
    server_sock.listen(128)
    
    try:
        while True:
            client_sock, client_addr = server_sock.accept()
            with client_sock:
                try:
                    header_bytes, rest_body = read_http_headers(client_sock)
                    method, path, version, headers = parse_http_request(header_bytes)
                    
                    content_length = int(headers.get("content-length", 0))
                    body = read_http_body(client_sock, rest_body, content_length) if content_length > 0 else b""
                    
                    # Маршрутизація
                    if method == "GET" and path == "/healthz":
                        payload = b'{"status": "healthy"}'
                        send_http_response(client_sock, 200, "OK",
                                           {"content-type": "application/json; charset=utf-8"}, payload)
                    elif method == "POST" and path == "/echo":
                        send_http_response(client_sock, 200, "OK",
                                           {"content-type": "application/octet-stream"}, body)
                    else:
                        payload = json.dumps({"error": "Resource not found", "path": path}).encode("utf-8")
                        send_http_response(client_sock, 404, "Not Found",
                                           {"content-type": "application/json; charset=utf-8"}, payload)
                except Exception as exc:
                    err_payload = json.dumps({"error": str(exc)}).encode("utf-8")
                    send_http_response(client_sock, 400, "Bad Request",
                                       {"content-type": "application/json; charset=utf-8"}, err_payload)
    finally:
        server_sock.close()
```

## 2. Стандартна бібліотека: архітектура http.server та socketserver

Написання низькорівневого парсера вручну демонструє внутрішню фізику протоколу, однак створення надійного сервера вимагає обробки безлічі складних крайових випадків: складених багаторядкових заголовків (Obsolete Line Folding), підтримки постійних підключень (HTTP Keep-Alive), обробки помилок переповнення буферів і таймаутів сокета.

Стандартна бібліотека Python надає для цього ієрархію класів у модулях `socketserver` та `http.server`. Архітектурно система спирається на чітке розмежування двох сутностей: **мережевого сервера** (Server) та **обробника запитів** (Request Handler).

![Ієрархія класів socketserver та http.server у стандартній бібліотеці](/root/sys/sys-plang-python/http-server-minimal/img/http-server-class-hierarchy.svg)
*Ієрархія класів socketserver та http.server: поєднання серверного сокета з потоковими обробниками запитів та міксінами багатопотоковості.*

### Серверний транспорт: BaseServer, TCPServer та HTTPServer

1. **`socketserver.BaseServer`:**
   Визначає базовий абстрактний інтерфейс життєвого циклу сервера. Містить головний цикл `serve_forever()`, механізм диспетчеризації запитів `process_request()` та метод безпечної зупинки `shutdown()`.

2. **`socketserver.TCPServer`:**
   Реалізує транспортний рівень поверх протоколу TCP (сімейство `AF_INET`, тип `SOCK_STREAM`). У конструкторі виконує системні виклики `socket()`, `bind()` та `listen()`, зберігаючи дескриптор слухаючого сокета в атрибуті `self.socket`. Метод `get_request()` виконує виклик `accept()`, повертаючи пару `(client_socket, client_address)`.

3. **`http.server.HTTPServer`:**
   Успадковує `TCPServer` і додає специфічний для протоколу HTTP контекст: зберігає ім'я хоста `server_name` та номер порту `server_port`, які використовуються обробниками для побудови абсолютних посилань і перенаправлень.

### Обробка протоколу: BaseRequestHandler, StreamRequestHandler та BaseHTTPRequestHandler

Для кожного прийнятого клієнтського підключення сервер інстанціює новий екземпляр призначеного класу-обробника.

1. **`socketserver.BaseRequestHandler`:**
   Визначає каркас життєвого циклу обробника:
   - `setup()`: підготовка структур даних та потоків перед початком роботи;
   - `handle()`: виконання основної бізнес-логіки обробки;
   - `finish()`: закриття дескрипторів та звільнення виділених ресурсів після завершення запиту.

2. **`socketserver.StreamRequestHandler`:**
   Перевизначає метод `setup()`, обгортаючи сирий дескриптор сокета `self.request` у два зручні буферизовані потоки модуля `io`:
   - `self.rfile`: об'єкт `io.BufferedReader`, що дозволяє викликати `self.rfile.readline()` та `self.rfile.read(n)`;
   - `self.wfile`: об'єкт `io.BufferedWriter`, що дозволяє записувати вихідні дані методом `self.wfile.write(data)`.

3. **`http.server.BaseHTTPRequestHandler`:**
   Містить повноцінний синтаксичний парсер протоколу HTTP. У методі `handle()` обробник запускає цикл читання `handle_one_request()`. Метод зчитує стартовий рядок, розбирає заголовки у внутрішній об'єкт `http.client.HTTPMessage` (доступний через поле `self.headers`) і формує ім'я методу-обробника:

```python
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
```

### Практична реалізація власного обробника

Для створення функціонального сервера розробник створює підклас `BaseHTTPRequestHandler`, де описує методи `do_GET`, `do_POST` тощо, використовуючи стандартні хелпери формування заголовків:

```python
import json
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler

class DeviceMetricsHandler(BaseHTTPRequestHandler):
    # Примусово вмикаємо версію HTTP/1.1 для коректної обробки Keep-Alive
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:
        if self.path == "/api/v1/status":
            response_data = {"status": "operational", "load": 0.42}
            payload = json.dumps(response_data).encode("utf-8")
            
            # Формування статусного рядка та обов'язкових заголовків
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            
            # Запис тіла відповіді
            self.wfile.write(payload)
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Запитуваний ресурс не існує")

    def do_POST(self) -> None:
        if self.path == "/api/v1/telemetry":
            content_length_str = self.headers.get("Content-Length")
            if not content_length_str or not content_length_str.isdigit():
                self.send_error(HTTPStatus.LENGTH_REQUIRED, "Обов'язковий заголовок Content-Length")
                return
            
            content_length = int(content_length_str)
            body_bytes = self.rfile.read(content_length)
            
            try:
                data = json.loads(body_bytes.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.send_error(HTTPStatus.BAD_REQUEST, "Некоректний JSON-документ")
                return
            
            ack_payload = json.dumps({"status": "recorded", "received_keys": list(data.keys())}).encode("utf-8")
            
            self.send_response(HTTPStatus.CREATED)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(ack_payload)))
            self.end_headers()
            self.wfile.write(ack_payload)
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Запитуваний ресурс не існує")
```

Повний нормативний опис усіх полів обробника, правил роботи зі статусами `HTTPStatus` та механізмів обробки сокетних помилок наведено у довідковій вставці [Специфікація WSGI environ та API BaseHTTPRequestHandler](root:sys-plang-python/http-server-minimal/api-wsgi-environ.md).

### Проблема блокування та послідовного виконання

Базовий клас `http.server.HTTPServer` виконує весь цикл обробки строго синхронно в головному потоці процесу. Послідовність виглядає так:
1. `HTTPServer.serve_forever()` викликає блокувальний `accept()`;
2. Операційна система прокидає потік під час підключення клієнта A;
3. Екземпляр `DeviceMetricsHandler` починає вичитувати `self.rfile`;
4. Якщо клієнт A має повільне з'єднання (передає байти із затримкою в кілька секунд) або навмисно утримує з'єднання відкритим, головний потік сервера залишається заблокованим усередині виклику `rfile.read()`;
5. Клієнт B, який у цей самий час надсилає критичний запит `/healthz`, не може встановити з'єднання: його запит чекає у черзі TCP SYN Backlog ядра, а час очікування стрімко зростає.

## 3. Багатопотокова паралельність: socketserver.ThreadingMixIn

Для подолання проблеми однопотокового блокування стандартна бібліотека використовує архітектурний патерн Mixin, втілений у класі `socketserver.ThreadingMixIn`.

### Механіка ThreadingMixIn

Клас `ThreadingMixIn` змінює спосіб обробки прийнятого з'єднання. Замість безпосереднього виклику обробника в тому самому потоці, метод `process_request()` створює окремий потік операційної системи за допомогою модуля `threading.Thread`:

```python
# Концептуальна реалізація socketserver.ThreadingMixIn
class ThreadingMixIn:
    daemon_threads = True

    def process_request_thread(self, request, client_address):
        try:
            self.finish_request(request, client_address)
        except Exception:
            self.handle_error(request, client_address)
        finally:
            self.shutdown_request(request)

    def process_request(self, request, client_address):
        t = threading.Thread(target=self.process_request_thread,
                             args=(request, client_address))
        t.daemon = self.daemon_threads
        t.start()
```

Починаючи з версії Python 3.7, розробникам більше не потрібно збирати клас вручну: до модуля `http.server` включено готовий клас `ThreadingHTTPServer`, що поєднує `ThreadingMixIn` та `HTTPServer`:

```python
from http.server import ThreadingHTTPServer

def run_threaded_server():
    server_address = ("0.0.0.0", 8080)
    httpd = ThreadingHTTPServer(server_address, DeviceMetricsHandler)
    httpd.serve_forever()
```

### Ефективність потоків Python для мережевого вводу-виводу та роль GIL

Поширена хибна думка полягає в тому, що глобальне блокування інтерпретатора (GIL) у CPython робить використання потоків неефективним. Це твердження справедливе виключно для завдань, обмежених швидкістю процесора (CPU-bound, наприклад, математичні розрахунки або стиснення відео).

Для мережевих серверів характерне навантаження, обмежене швидкістю введення-виведення (I/O-bound): більшу частину часу потік проводить в очікуванні надходження байтів із мережевого кабелю або скидання буфера в мережевий стек.

Усі мережеві системні виклики CPython (`accept`, `recv`, `sendall`, `select`, `poll`) реалізовані мовою C у модулі `Modules/socketmodule.c`. Перед виконанням блокувального виклику ядра інтерпретатор викликає макрос `Py_BEGIN_ALLOW_THREADS`, який **повністю відпускає GIL**.

Поки потік 1 заблокований ядром ОС в очікуванні даних від повільного датчика, інші потоки Python можуть вільно захоплювати GIL, виконувати маршрутизацію, парсити JSON або відправляти відповіді іншим клієнтам. Це забезпечує ефективну паралелізацію обробки тисяч одночасних запитів без значного процесорного оверхеду.

### Синхронізація спільного стану між потоками

Оскільки кожен запит обробляється у власному системному потоці, спільні структури даних програми (лічильники запитів, буфери останніх вимірювань датчиків, кеші в оперативній пам'яті) стають спільним ресурсом. Несинхронізований доступ до спільних змінних викликає стан гонитви (Race Condition):

```python
import threading
import time

class ThreadSafeTelemetryRegistry:
    """Потокобезпечний реєстр телеметрії з гранулярним блокуванням."""
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._records: dict[str, dict] = {}
        self._request_counter = 0

    def register_metric(self, sensor_id: str, value: float) -> None:
        with self._lock:
            self._request_counter += 1
            self._records[sensor_id] = {
                "val": value,
                "ts": time.time()
            }

    def get_aggregated_snapshot(self) -> dict:
        with self._lock:
            # Створюємо поверхневу копію словника для безпечної серіалізації в JSON
            # без блокування реєстру на час відправки даних у мережу
            return {
                "total_processed": self._request_counter,
                "sensors": dict(self._records)
            }
```

## 4. Специфікація WSGI (PEP 3333): універсальний інтерфейс вебзастосунків

Пряме використання класів `BaseHTTPRequestHandler` створює жорстку прив'язку бізнес-логіки до внутрішньої реалізації конкретного сервера зі стандартної бібліотеки. Якщо проєкту знадобиться перехід на виробничий багатопроцесний сервер (Gunicorn, uWSGI) або підключення готових бібліотек авторизації, весь код доведеться переписувати.

Для вирішення цієї проблеми було розроблено стандарт **WSGI (Web Server Gateway Interface, PEP 3333)** — єдиний універсальний протокол взаємодії між вебсерверами та вебзастосунками на мові Python. Історію виникнення цього стандарту та його еволюцію детально розглянуто у вставці [Історія веб-інтерфейсів у Python: від CGI до WSGI та ASGI](root:sys-plang-python/http-server-minimal/hist-wsgi-evolution.md).

![Конвеєр WSGI: поділ транспорту, проміжного шару та бізнес-додатка](/root/sys/sys-plang-python/http-server-minimal/img/wsgi-architecture-pipeline.svg)
*Конвеєр WSGI (PEP 3333): сервер створює словник environ та колбек start_response, передає їх через ланцюжок Middleware у застосунок, який повертає ітерований потік байтів.*

### Контракт WSGI-застосунку

Згідно зі стандартом PEP 3333, коректним WSGI-застосунком є будь-який об'єкт Python, що підтримує виклик (`Callable`), який приймає два позиційні аргументи:
1. `environ`: словник `dict`, що містить змінні запиту в стилі CGI та спеціальні змінні середовища з префіксом `wsgi.*`;
2. `start_response`: функція зворотного виклику, надана сервером, яка приймає статус відповіді та список заголовків.

Застосунок зобов'язаний повернути ітерований об'єкт, кожен елемент якого є двійковим масивом `bytes`:

```python
def simple_wsgi_application(environ: dict, start_response) -> list[bytes]:
    status = "200 OK"
    response_headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Cache-Control", "no-cache"),
    ]
    
    # Викликаємо функцію реєстрації статусу та заголовків
    start_response(status, response_headers)
    
    # Повертаємо тіло як список байтових фрагментів
    return [b'{"engine": "WSGI PEP 3333", "status": "ready"}']
```

### Синтаксичний розбір параметрів через environ

Словник `environ` містить усю інформацію про вхідний HTTP-запит:
- `environ['REQUEST_METHOD']`: назва методу (`"GET"`, `"POST"`);
- `environ['PATH_INFO']`: шлях до ресурсу всередині застосунку (наприклад, `"/api/v1/sensors"`);
- `environ['QUERY_STRING']`: рядок параметрів запиту після символу `?`;
- `environ['wsgi.input']`: бінарний файлоподібний потік читання, з якого вичитується тіло запиту за лімітом `CONTENT_LENGTH`.

Приклад диспетчеризації запитів та обробки вхідного JSON-навантаження:

```python
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
```

### Патерн WSGI Middleware (Проміжний шар)

Завдяки уніфікації інтерфейсу між сервером і застосунком можна вбудовувати довільну кількість проміжних обробників (Middleware). Проміжний шар виступає одночасно як застосунок для сервера і як сервер для кінцевого застосунку:

```python
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
```

### Запуск через вбудований модуль wsgiref

Для запуску WSGI-застосунку без сторонніх залежностей стандартна бібліотека надає модуль `wsgiref.simple_server`:

```python
from wsgiref.simple_server import make_server

if __name__ == "__main__":
    app_pipeline = RequestTimingMiddleware(router_wsgi_app)
    with make_server("127.0.0.1", 8080, app_pipeline) as httpd:
        print("WSGI сервер успішно запущено на порту 8080...")
        httpd.serve_forever()
```

## 5. Практична реалізація: автономний мікросервер телеметрії з JSON API

Нижче наведено повну реалізацію автономного виробничого мікросервера збору телеметрії. Сервер спроєктовано для роботи у вбудованих Linux-системах та IoT-шлюзах, він не має зовнішніх залежностей від сторонніх пакетів, підтримує потокобезпечне накопичення показників датчиків, захист від переповнення буферів, перевірку життєздатності (Liveness Probe) та коректне завершення роботи (Graceful Shutdown) при отриманні сигналів операційної системи `SIGINT` або `SIGTERM`.

### Архітектура та повний вихідний код мікросервера

```python
import json
import signal
import sys
import threading
import time
from http import HTTPStatus
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Any


class TelemetryDataStore:
    """Потокобезпечне сховище останніх показників датчиків та агрегованих метрик."""
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._start_time = time.time()
        self._total_requests_count = 0
        self._devices_telemetry: dict[str, dict[str, Any]] = {}

    def record_device_telemetry(self, device_id: str, payload: dict[str, Any]) -> None:
        with self._lock:
            self._total_requests_count += 1
            self._devices_telemetry[device_id] = {
                "metrics": payload,
                "updated_at": time.time(),
            }

    def get_system_snapshot(self) -> dict[str, Any]:
        with self._lock:
            self._total_requests_count += 1
            uptime = time.time() - self._start_time
            return {
                "status": "healthy",
                "uptime_seconds": round(uptime, 2),
                "total_http_requests": self._total_requests_count,
                "registered_devices_count": len(self._devices_telemetry),
                "devices": dict(self._devices_telemetry),
            }


# Глобальний екземпляр сховища стану
TELEMETRY_STORE = TelemetryDataStore()


class TelemetryMicroserverHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _write_json_response(self, status: HTTPStatus, data: dict[str, Any]) -> None:
        """Допоміжний метод формування та відправки JSON-відповіді з коректними заголовками."""
        try:
            payload = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        except TypeError as err:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Помилка серіалізації: {err}")
            return

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        if self.path == "/healthz":
            # Ендпоінт перевірки працездатності для Docker або Kubernetes Liveness Probe
            self._write_json_response(HTTPStatus.OK, {
                "service": "telemetry-node",
                "status": "healthy"
            })
        elif self.path in ("/metrics", "/api/v1/metrics"):
            # Ендпоінт моніторингу та агрегованого стану пристроїв
            snapshot = TELEMETRY_STORE.get_system_snapshot()
            self._write_json_response(HTTPStatus.OK, snapshot)
        else:
            self._write_json_response(HTTPStatus.NOT_FOUND, {
                "error": "Not Found",
                "message": f"Ендпоінт '{self.path}' не знайдено",
                "status_code": 404
            })

    def do_POST(self) -> None:
        if self.path in ("/telemetry", "/api/v1/telemetry"):
            content_length_header = self.headers.get("Content-Length")
            if not content_length_header or not content_length_header.isdigit():
                self._write_json_response(HTTPStatus.LENGTH_REQUIRED, {
                    "error": "Length Required",
                    "message": "Запит повинен містити числовий заголовок Content-Length"
                })
                return

            payload_length = int(content_length_header)
            # Захист від атак вичерпання пам'яті: обмежуємо корисне навантаження 64 кілобайтами
            max_allowed_payload = 65536
            if payload_length > max_allowed_payload:
                self._write_json_response(HTTPStatus.PAYLOAD_TOO_LARGE, {
                    "error": "Payload Too Large",
                    "message": f"Розмір тіла перевищує ліміт {max_allowed_payload} байтів"
                })
                return

            body_bytes = self.rfile.read(payload_length)
            try:
                parsed_payload = json.loads(body_bytes.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as parse_err:
                self._write_json_response(HTTPStatus.BAD_REQUEST, {
                    "error": "Bad Request",
                    "message": "Неможливо розібрати JSON-документ",
                    "details": str(parse_err)
                })
                return

            # Валідація схеми корисного навантаження
            device_id = parsed_payload.get("device_id")
            metrics_data = parsed_payload.get("metrics")

            if not device_id or not isinstance(device_id, str):
                self._write_json_response(HTTPStatus.UNPROCESSABLE_ENTITY, {
                    "error": "Unprocessable Entity",
                    "message": "Поле 'device_id' є обов'язковим непорожнім рядком"
                })
                return

            if not metrics_data or not isinstance(metrics_data, dict):
                self._write_json_response(HTTPStatus.UNPROCESSABLE_ENTITY, {
                    "error": "Unprocessable Entity",
                    "message": "Поле 'metrics' є обов'язковим об'єктом показників"
                })
                return

            # Атомарний запис у сховище
            TELEMETRY_STORE.record_device_telemetry(device_id, metrics_data)
            
            self._write_json_response(HTTPStatus.CREATED, {
                "status": "success",
                "device_id": device_id,
                "recorded_at": time.time()
            })
        else:
            self._write_json_response(HTTPStatus.NOT_FOUND, {
                "error": "Not Found",
                "message": f"Ендпоінт '{self.path}' не знайдено",
                "status_code": 404
            })

    def log_message(self, format_string: str, *args) -> None:
        """Перевизначення стандартного формату логування для чіткого моніторингу запитів."""
        client_ip, client_port = self.client_address
        log_entry = f"[{self.log_date_time_string()}] {client_ip}:{client_port} - {format_string % args}\n"
        sys.stdout.write(log_entry)
        sys.stdout.flush()


def run_standalone_telemetry_microserver(host: str = "0.0.0.0", port: int = 8080) -> None:
    """Запуск сервера у фоновому потоці з підтримкою Graceful Shutdown."""
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, TelemetryMicroserverHandler)
    
    # Запускаємо цикл прийому з'єднань у виділеному потоці
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=False)
    server_thread.start()
    print(f"Сервер телеметрії успішно запущено за адресою http://{host}:{port}")

    shutdown_trigger = threading.Event()

    def handle_termination_signal(signum: int, frame) -> None:
        print(f"\nОтримано системний сигнал ({signum}), ініціалізація коректної зупинки сервера...")
        shutdown_trigger.set()

    # Реєструємо перехоплення сигналів завершення
    signal.signal(signal.SIGINT, handle_termination_signal)
    signal.signal(signal.SIGTERM, handle_termination_signal)

    # Очікування сигналу завершення в головному потоці
    while not shutdown_trigger.is_set():
        shutdown_trigger.wait(timeout=0.5)

    print("Зупинка обробки нових TCP-з'єднань...")
    httpd.shutdown()
    server_thread.join()
    httpd.server_close()
    print("Сервер повністю зупинено. Мережеві сокети звільнено.")


if __name__ == "__main__":
    run_standalone_telemetry_microserver()
```
