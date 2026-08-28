# Flask і FastAPI

<preknowlist>
- [Цикл подій asyncio](root:sys-plang-python/asyncio-event-loop) — кооперативна багатозадачність, черга задач та мультиплексування вводу-виводу.
- [Корутини й await](root:sys-plang-python/coroutines-and-await) — асинхронні функції, механізм призупинення виконання та повернення керування.
- [Потоки в I/O та CPU-задачах](root:sys-plang-python/threads-io-vs-cpu-bound) — накладні витрати системних потоків та блокування інтерпретатора.
- [Найпростіший HTTP-сервер](root:sys-plang-python/http-server-minimal) — протокол HTTP, структура заголовків, формат тіла та коди відповідей.
</preknowlist>

Шлюз збору телеметрії промислового підприємства опитує 5 000 польових датчиків вібрації та температури, щомиті відправляючи пакети вимірювань через протокол HTTP POST на бекенд-сервер. Якщо обробник записує кожне вимірювання в реляційну базу даних із мережевою затримкою 15 мілісекунд, класичний синхронний сервер на базі 16 робочих процесів вичерпує пул обробки вже при 1 000 одночасних запитах: черга з'єднань переповнюється, затримка відповіді підскакує з 15 мілісекунд до 4 секунд, а вхідні пакети телеметрії масово відкидаються за таймаутом.

Ця криза пропускної здатності виникає не через брак обчислювальної потужності процесора, а через фундаментальну невідповідність між синхронною моделлю виконання («один системний потік на одне блокувальне з'єднання») та характером мережевого навантаження сучасних систем інтернету речей (англ. *Internet of Things*, IoT). Порівняння мікрофреймворку Flask та асинхронного фреймворку FastAPI розкриває два принципово різні підходи до керування системними ресурсами, валідації вхідних даних та організації життєвого циклу веб-додатків у Python.

## Архітектурні моделі: WSGI проти ASGI

В основі різниці між Flask і FastAPI лежить протокол взаємодії між веб-сервером операційної системи та виконуваним кодом додатку на Python.

```
WSGI (PEP 3333):   Клієнт ──► Gunicorn Master ──► Worker Process/Thread (Блокується на I/O) ──► Flask
ASGI (ASGI 3.0):   Клієнт ──► Uvicorn (uvloop) ──► Single-Thread Event Loop (Корутини)   ──► FastAPI
```

Історичний розвиток інтерфейсів від ранніх CGI-скриптів до сучасних асинхронних шлюзів детально описано у вставці [📜 Від CGI та WSGI до ASGI: еволюція веб-інтерфейсів Python](root:sys-plang-python/flask-and-fastapi/hist-wsgi-to-asgi.md).

### Синхронний контракт WSGI та ціна блокування

Flask реалізує інтерфейс WSGI (англ. *Web Server Gateway Interface*, PEP 3333). Додаток є синхронним викликальним об'єктом із сигнатурою:

```py
def application(environ: dict, start_response: callable) -> list[bytes]:
    ...
```

Коли виробничий сервер (наприклад, Gunicorn або uWSGI) отримує вхідне TCP-з'єднання, він передає керування функції додатку всередині виділеного системного процесу або потоку ОС (`pthread`). Усі операції всередині цього виклику — парсинг заголовків, декодування JSON-пакета від сенсора, виконання SQL-запиту, очікування відповіді від Redis — відбуваються послідовно та блокувально.

Поки обробник очікує завершення дискового чи мережевого вводу-виводу (I/O Wait), системний потік перебуває в стані очікування ядра ОС (`TASK_INTERRUPTIBLE`). Інтерпретатор CPython не може використати цей потік для обробки наступного клієнта. Для забезпечення паралелізму сервер змушений підтримувати пул із десятків або сотень процесів чи потоків.

Такий підхід створює критичні накладні витрати пам'яті та процесора:
1. **Виділення оперативної пам'яті**: кожен окремий процес CPython вимагає 30–60 МБ пам'яті для завантаження коду та бібліотек. Якщо замість процесів використовуються системні потоки, кожен потік резервує під власний стек викликів від 2 до 8 МБ пам'яті ядра ОС (`ulimit -s`).
2. **Перемикання контексту ядра (Context Switching)**: коли сотні потоків одночасно змагаються за процесорний час під час надходження мережевих пакетів, ядро операційної системи витрачає значну частку тактів на збереження та відновлення регістрів ЦП і скидання кешів процесора (TLB flush).
3. **Обмеження C10k**: утримання 10 000 відкритих TCP-з'єднань (наприклад, для пристроїв, що транслюють потокові дані або використовують тривале опитування) вимагало б 10 000 системних потоків, що гарантовано призводить до аварійного вичерпання дескрипторів пам'яті ядра (`OOM Killer`).

### Асинхронний контракт ASGI та мультиплексування сокетів

FastAPI побудований на базі асинхронного стандарту ASGI (англ. *Asynchronous Server Gateway Interface* 3.0) та інструментарію Starlette. Додаток являє собою асинхронну корутину:

```py
async def application(scope: dict, receive: callable, send: callable) -> None:
    ...
```

Повний опис структур словників `environ` та `scope`, а також протоколів повідомлень наведено у довіднику [📋 Специфікація WSGI та ASGI: протокольні контракти серверів](root:sys-plang-python/flask-and-fastapi/api-framework-contracts.md).

Сервер ASGI промислового рівня (Uvicorn або Granian) запускає цикл подій (англ. *event loop*) на базі `uvloop` — високопродуктивної C-обгортки над системною бібліотекою `libuv`. Сервер використовує механізм системного мультиплексування сокетів ядра Linux (`epoll`) або macOS/BSD (`kqueue`):

![Архітектурні моделі WSGI та ASGI](/root/sys/sys-plang-python/flask-and-fastapi/img/wsgi-vs-asgi-architecture.svg)
*Архітектурне порівняння WSGI з пулом синхронних процесів/потоків та ASGI з єдиним циклом подій.*

Замість виділення окремого системного потоку на кожного клієнта, Uvicorn реєструє тисячі відкритих файлових дескрипторів сокетів в одному системному виклику `epoll_wait()`. Коли від датчика надходить порція байтів, ядро ОС пробуджує цикл подій. Сервер створює легковажний об'єкт корутини (англ. *Task*) у пам'яті інтерпретатора.

Коли корутина доходить до операції введення-виведення (наприклад, виконання асинхронного SQL-запиту через драйвер `asyncpg`):

```py
await db.execute("INSERT INTO sensor_log VALUES ($1, $2)", sensor_id, val)
```

Оператор `await` призупиняє виконання поточної задачі та повертає керування в цикл подій. Поки мережевий сокет бази даних передає байти по дротах, цикл подій за мікросекунди бере з черги `epoll` пакети від десятків інших датчиків. 

Накладні витрати на корутину в пам'яті складають лише 2–4 КБ (проти 8 МБ системного стеку потоку), а перемикання між задачами відбувається повністю всередині простору користувача без викликів ядра ОС і без скидання процесорних кешів.

## Маршрутизація та валідація даних сенсорів

Системи збору телеметрії висувають жорсткі вимоги до обробки структур даних: повідомлення від апаратних датчиків надходять у вигляді сирих JSON-об'єктів або бінарних пакетів, які необхідно декодувати, перевірити на відповідність діапазонам фізичних величин (температура не нижче абсолютного нуля, вологість від 0 до 100%) та перетворити на типізовані структури.

### Маршрутизація: Werkzeug проти Starlette

У Flask диспетчеризація запитів виконується маршрутизатором бібліотеки Werkzeug. Маршрути зберігаються у структурі `Map` у вигляді списку правил `Rule`. Кожне правило компілюється в регулярний вираз. Під час надходження запиту сервер послідовно порівнює `PATH_INFO` з регулярними виразами. При зростанні кількості ендпоінтів до сотень час пошуку маршруту зростає лінійно, якщо не застосовується оптимізація префіксних дерев.

У FastAPI маршрутизація реалізована через `APIRouter` бібліотеки Starlette. Маршрути організовані в оптимізований префіксний граф. Диспетчер аналізує шлях за сегментами без перебору невідповідних гілок.

Крім того, FastAPI на етапі ініціалізації аналізує сигнатуру кожного обробника через модуль `inspect`, будуючи статичну схему вилучення параметрів (з URL-шляху, параметрів запиту `query`, заголовків `headers`, cookies та тіла `body`).

### Валідація: динамічний Python проти скомпільованого Rust ядра

У класичному додатку на Flask розробник змушений проводити валідацію вручну або інтегрувати зовнішні бібліотеки на зразок Marshmallow чи Cerberus:

```py
# Підхід Flask з ручною валідацією або Marshmallow
@app.route("/api/v1/telemetry", methods=["POST"])
def ingest():
    data = request.get_json()
    if not data or "device_id" not in data or "temperature" not in data:
        return jsonify({"error": "Bad Request", "details": "Missing fields"}), 400
    
    # Ручна перевірка типів та меж значень
    try:
        temp = float(data["temperature"])
        if not (-50.0 <= temp <= 150.0):
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"error": "Validation Error", "field": "temperature"}), 422
```

Такий підхід має три суттєві недоліки:
1. **Високі накладні витрати на інтерпретацію**: виконання тисяч перевірок `isinstance()`, блоків `try-except` та викликів динамічних методів у чистому байткоді Python сповільнює обробку кожного пакета на сотні мікросекунд.
2. **Відсутність єдиного джерела правди**: типи для валідації існують окремо від анотацій типів коду, що веде до помилок типізації при рефакторингу.
3. **Дублювання коду документації**: для опису структури в документації API доводиться окремо підтримувати схеми Swagger.

FastAPI використовує бібліотеку Pydantic v2. Починаючи з версії 2.0, усе ядро валідації, парсингу та серіалізації Pydantic повністю переписано мовою Rust під назвою `pydantic-core`.

![Конвеєр прийому телеметрії](/root/sys/sys-plang-python/flask-and-fastapi/img/telemetry-processing-pipeline.svg)
*Конвеєр обробки пакетів телеметрії у FastAPI: від системного виклику epoll до валідації в Rust-ядрі Pydantic.*

Коли JSON-байти надходять у FastAPI:
1. Сирий потік байтів передається безпосередньо у C-розширення `pydantic-core` без попереднього створення проміжних словників Python.
2. Rust-парсер одночасно перевіряє типи даних, межі діапазонів (`ge`, `le`), відповідність регулярним виразам і парсить рядки дат стандарту ISO 8601 у нативні структури CPython.
3. Валідація виконується в 5–15 разів швидше, ніж аналогічна валідація на чистому Python.
4. У разі невідповідності формату FastAPI автоматично повертає стандартизовану відповідь із кодом `422 Unprocessable Entity`, де вказано точний шлях до помилкового поля в JSON-документі.

```py
from pydantic import BaseModel, Field
from datetime import datetime

class SensorReading(BaseModel):
    device_id: str = Field(min_length=4, max_length=32, pattern=r"^[a-zA-Z0-9_-]+$")
    timestamp: datetime
    temperature: float = Field(ge=-50.0, le=150.0, description="Температура сенсора в °C")
    humidity: float = Field(ge=0.0, le=100.0, description="Відносна вологість у %")
    battery_mv: int = Field(ge=0, le=4500, description="Напруга елемента живлення в мВ")
```

### Керування залежностями: ContextVar проти Dependency Injection

Архітектура Flask покладається на глобальні контекстні змінні `request`, `g` та `session`. Під капотом Flask використовує об'єкти `werkzeug.local.LocalProxy`, які звертаються до механізму `contextvars.ContextVar`.

Це створює неявні глобальні стани:
* Функція бізнес-логіки змушена імпортувати глобальний `request`, що ускладнює її ізольоване тестування без створення фіктивного контексту запиту (`app.test_request_context()`).
* При передачі обробки у фоновий потік або асинхронну задачу контекст запиту губиться, якщо його не скопіювати вручну через `copy_context()`.

FastAPI реалізує патерн впровадження залежностей (англ. *Dependency Injection*, лат. *dependentia* — залежність) через декларативний механізм `Depends()`:

```py
from fastapi import Depends, Header, HTTPException, status

async def verify_device_token(x_device_token: str = Header(...)) -> str:
    # Перевірка криптографічного токена датчика в асинхронному кеші
    if not await token_cache.is_valid(x_device_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid device hardware token"
        )
    return x_device_token

@app.post("/api/v1/telemetry")
async def record_telemetry(
    reading: SensorReading,
    token: str = Depends(verify_device_token),
    db: AsyncSession = Depends(get_db_session)
):
    await db.save(reading)
    return {"status": "accepted"}
```

Механізм `Depends()` будує орієнтований ациклічний граф (DAG) залежностей для кожного запиту:
1. Залежності можуть виконуватися ієрархічно (залежність залежності).
2. Залежності, що повторюються в межах одного запиту, автоматично кешуються (`use_cache=True`), уникаючи повторних звернень до бази даних чи розрахунків токенів.
3. Підтримується автоматичне керування ресурсами через контекстні менеджери `async with` (наприклад, відкриття транзакції бази даних перед викликом ендпоінта та її гарантований commit/rollback після завершення).
4. Під час модульного тестування будь-яку системну залежність (наприклад, реальне підключення до БД) можна перекрити одним рядком через `app.dependency_overrides[get_db_session] = fake_session`.

## Продуктивність і поведінка під навантаженням

Для порівняння характеристик синхронної та асинхронної моделей розглянемо поведінку тестового стенду під час обробки пакетів телеметрії. Повний код навантажувального генератора та конфігурації серверів наведено у проекті [⚙️ Бенчмаркінг та навантажувальне тестування IoT-бекендів](root:sys-plang-python/flask-and-fastapi/proj-iot-telemetry-bench.md).

![Масштабованість затримок і пам'яті](/root/sys/sys-plang-python/flask-and-fastapi/img/concurrency-memory-latency.svg)
*Залежність P99 latency та споживання оперативної пам'яті від кількості одночасних з'єднань.*

### Математика затримок черги у синхронному сервері

Нехай сервер Flask запущено під керуванням Gunicorn з `N = 8` робочими процесами. Кожен запит записує телеметрію в базу даних за час `T_io = 15` мілісекунд (0.015 секунди).

Максимальна теоретична пропускна здатність системи без урахування накладних витрат на серіалізацію складає:

```
RPS_max = N / T_io
        = 8 / 0.015
        ≈ 533.3 запитів/с
```

Якщо 1 000 датчиків одночасно надсилають вимірювання:
* Перші 8 запитів миттєво займають усі 8 робочих процесів.
* Решта 992 запити потрапляють у системну чергу очікування сокета (параметр ядра `listen(..., backlog)`).
* Середній час очікування в черзі для останнього запиту складе:

```
T_wait = (992 · 0.015) / 8
       ≈ 1.86 секунди
```

Затримка відповіді для датчика зростає з базових 15 мс до 1.875 секунди. Якщо кількість датчиків зростає до 5 000, час очікування перевищує типові клієнтські таймаути (5 секунд), виникає явище каскадного перевантаження (англ. *retry storm*), черга TCP переповнюється, і сервер починає відкидати запити з помилками `504 Gateway Timeout` або `Connection Refused`.

### Поведінка асинхронного сервера

У FastAPI під керуванням Uvicorn на базі 1 процесорного ядра:
* Коли запит починає очікувати відповідь від бази даних через `await db.execute()`, корутина поступається місцем у циклі подій.
* Одне ядро процесора займається виключно корисною роботою: парсингом JSON через `pydantic-core`, валідацією та упаковкою SQL-команд у буфери сокетів.
* Пропускна здатність обмежується лише швидкістю серіалізації даних на CPU та мережевою смугою бази даних, досягаючи 15 000–35 000 запитів на секунду на процес.
* Затримка P99 залишається стабільною в діапазоні 20–40 мс навіть при 10 000 одночасних з'єднань.

### Пастка блокувального коду в асинхронному циклі

Головною небезпекою при роботі з асинхронними фреймворками є випадковий виклик синхронної блокувальної функції всередині корутини:

```py
# КРИТИЧНА ПОМИЛКА: блокування всього циклу подій
@app.post("/api/v1/telemetry")
async def bad_handler(data: SensorReading):
    # Блокувальний системний виклик або синхронний клієнт requests
    time.sleep(0.05)  # Заблокує обробку ВСІХ 10 000 клієнтів на 50 мс!
    return {"status": "ok"}
```

Якщо в тілі функції `async def` викликати `time.sleep()`, синхронний клієнт `requests.get()` або важкий обчислювальний алгоритм (наприклад, розрахунок криптографічного хешу PBKDF2), системний потік зупиняється. Цикл подій не може виконати жодної іншої задачі, і сервер повністю паралізується для всіх підключених сенсорів.

FastAPI пропонує елегантне рішення для інтеграції синхронного коду. Якщо ендпоінт оголошено зі звичайним ключовим словом `def` (без `async`):

```py
# БЕЗПЕЧНО: FastAPI автоматично виносить функцію в окремий потік
@app.post("/api/v1/telemetry-sync")
def sync_handler(data: SensorReading):
    # Виконується всередині ThreadPoolExecutor
    time.sleep(0.05)
    return {"status": "ok"}
```

FastAPI виявляє синхронну сигнатуру через інтроспекцію і автоматично делегує виконання функції в системний пул потоків через `anyio.to_thread.run_sync()`, запобігаючи зупинці основного циклу подій.

## Специфікація OpenAPI та генерація клієнтських SDK

У складних розподілених системах інтернету речей важливим фактором є синхронізація контрактів між сервером прийому даних, польовими шлюзами та панелями моніторингу.

### Автоматична генерація схем у FastAPI

FastAPI проектувався навколо стандарту OpenAPI (раніше відомого як Swagger) та JSON Schema. Оскільки всі вхідні параметри, вихідні моделі та помилки типізуються за допомогою Pydantic і стандартних анотацій типів Python, фреймворк генерує вичерпну специфікацію `openapi.json` під час старту додатку:

```
FastAPI Додаток ──► Інтроспекція Pydantic/Type Hints ──► Специфікація OpenAPI 3.1
                                                               │
                    ┌──────────────────────────────────────────┴────────────────────────┐
                    ▼                                                                   ▼
       Інтерактивний Swagger UI (/docs)                                 OpenAPI Generator CLI
       та ReDoc UI (/redoc)                                            (Генерація C++/Rust SDK)
```

Це надає інженерні переваги:
1. **Інтерактивна документація «з коробки»**: за адресою `/docs` доступний Swagger UI, що дозволяє тестувати відправку пакетів телеметрії безпосередньо з браузера з валідацією полів у реальному часі.
2. **Усунення розсинхронізації схем (Schema Drift)**: документація не пишеться вручну у відокремлених файлах YAML/Markdown — вона є прямим результатом виконуваного коду. Зміна назви поля чи типу в Pydantic-моделі миттєво оновлює OpenAPI схему.
3. **Автоматична кодогенерація для пристроїв IoT**: на основі `openapi.json` за допомогою інструменту `openapi-generator-cli` можна автоматично згенерувати типізований клієнтський код мовами C++, Embedded Rust або MicroPython для прошивки мікроконтролерів (ESP32, STM32).

### Ситуація з документацією у Flask

У Flask підтримка OpenAPI не є базовою функцією. Для її реалізації застосовують сторонні бібліотеки:
* **Flasgger**: вимагає написання документації у вигляді YAML-блоків у docstrings функцій. Будь-яка помилка відступів ламає парсер, а типи в YAML часто не збігаються з реальною логікою валідації в коді Python.
* **Flask-RESTX / Flask-OpenAPI3**: додають власні шари абстракцій та специфічні класи моделей, перетворюючи Flask на інший діалект і вимагаючи подвійного опису структур даних.

## Реалізація IoT-бекенду прийому телеметрії

Для наочного порівняння розглянемо практичну реалізацію повноцінного сервісу прийому пакетів телеметрії з польових метеостанцій на обох фреймворках.

Кожен пакет містить:
* Ідентифікатор пристрою (`device_id`).
* Мітку часу заміру (`timestamp`).
* Температуру навколишнього середовища (`temperature`).
* Відносну вологість (`humidity`).
* Атмосферний тиск (`pressure_hpa`).
* Напругу батареї (`battery_mv`).

### Реалізація на Flask

```py
import os
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request, g

app = Flask(__name__)
DATABASE_PATH = os.getenv("DB_PATH", "telemetry_flask.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                pressure_hpa REAL NOT NULL,
                battery_mv INTEGER NOT NULL
            )
        """)

@app.route("/api/v1/telemetry", methods=["POST"])
def ingest_telemetry():
    # 1. Перевірка заголовка авторизації
    token = request.headers.get("X-Sensor-Token")
    if token != "secret-station-token":
        return jsonify({"error": "Unauthorized"}), 401

    # 2. Отримання та парсинг JSON
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON format"}), 400

    # 3. Ручна валідація полів
    required_fields = ["device_id", "timestamp", "temperature", "humidity", "pressure_hpa", "battery_mv"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 422

    device_id = str(data["device_id"])
    try:
        ts = datetime.fromisoformat(data["timestamp"])
        temp = float(data["temperature"])
        hum = float(data["humidity"])
        press = float(data["pressure_hpa"])
        batt = int(data["battery_mv"])
    except (ValueError, TypeError) as exc:
        return jsonify({"error": "Data type validation failed", "details": str(exc)}), 422

    if not (-50.0 <= temp <= 85.0) or not (0.0 <= hum <= 100.0) or not (300.0 <= press <= 1200.0):
        return jsonify({"error": "Sensor value out of physical bounds"}), 422

    # 4. Запис у базу даних
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO telemetry (device_id, timestamp, temperature, humidity, pressure_hpa, battery_mv)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (device_id, ts.isoformat(), temp, hum, press, batt))
    db.commit()

    return jsonify({"status": "success", "id": cursor.lastrowid}), 201

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000)
```

Запуск у виробничому середовищі під Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 flask_backend:app
```

### Реалізація на FastAPI

```py
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated
import aiosqlite
from fastapi import FastAPI, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

DATABASE_PATH = "telemetry_fastapi.db"

# 1. Pydantic-моделі вхідних даних та відповідей
class TelemetryPayload(BaseModel):
    device_id: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_\-]+$")
    timestamp: datetime
    temperature: float = Field(ge=-50.0, le=85.0, description="Температура сенсора в °C")
    humidity: float = Field(ge=0.0, le=100.0, description="Відносна вологість у %")
    pressure_hpa: float = Field(ge=300.0, le=1200.0, description="Атмосферний тиск у гПа")
    battery_mv: int = Field(ge=0, le=5000, description="Напруга живлення в мВ")

class IngestResponse(BaseModel):
    status: str
    record_id: int
    received_at: datetime

# 2. Керування життєвим циклом додатку (Lifespan Context)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ініціалізація структури бази даних під час старту
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                pressure_hpa REAL NOT NULL,
                battery_mv INTEGER NOT NULL
            )
        """)
        await db.commit()
    yield
    # Очищення ресурсів під час зупинки сервісу

app = FastAPI(
    title="IoT Industrial Telemetry Ingestion API",
    version="1.0.0",
    lifespan=lifespan
)

# 3. Впровадження залежностей (Dependency Injection)
async def verify_auth_token(x_sensor_token: Annotated[str, Header()]) -> str:
    if x_sensor_token != "secret-station-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Sensor-Token header"
        )
    return x_sensor_token

async def get_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        yield db

# 4. Асинхронний ендпоінт прийому телеметрії
@app.post(
    "/api/v1/telemetry",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Прийом вимірювань сенсорної станції"
)
async def ingest_telemetry(
    payload: TelemetryPayload,
    _: Annotated[str, Depends(verify_auth_token)],
    db: Annotated[aiosqlite.Connection, Depends(get_db)]
):
    cursor = await db.execute("""
        INSERT INTO telemetry (device_id, timestamp, temperature, humidity, pressure_hpa, battery_mv)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        payload.device_id,
        payload.timestamp.isoformat(),
        payload.temperature,
        payload.humidity,
        payload.pressure_hpa,
        payload.battery_mv
    ))
    await db.commit()

    return IngestResponse(
        status="success",
        record_id=cursor.lastrowid,
        received_at=datetime.utcnow()
    )
```

Запуск у виробничому середовищі під Uvicorn:

```bash
uvicorn fastapi_backend:app --host 0.0.0.0 --port 8000 --workers 4 --loop uvloop --http httptools
```

## Розгортання у промисловому середовищі: супервізори та зворотні проксі

Для досягнення максимальної відмовостійкості та продуктивності в реальних IoT-кластерах сервіси на базі Flask або FastAPI розгортаються за багаторівневою схемою:

```
[IoT Сенсори] ──► [Nginx / Traefik (TLS, Rate Limit, Buffering)] ──► [Gunicorn Master (Supervisor)] ──► [4x Uvicorn Workers]
```

### 1. Роль Nginx як зворотного проксі (Reverse Proxy)

Nginx встановлюється перед серверами додатків для виконання критичних інфраструктурних завдань:
* **Термінація TLS/SSL**: шифрування трафіку вимагає значних ресурсів CPU. Перенесення криптографічних операцій на Nginx (з апаратною акселерацією AES-NI) звільняє інтерпретатор Python від обчислень handshake.
* **Буферизація повільних клієнтів (Slowloris Protection)**: польові пристрої на слабких каналах зв'язку (GPRS, LoRaWAN через IP-шлюзи) можуть передавати 200 байт JSON протягом кількох секунд. Nginx вичитує тіло запиту у власний буфер і передає його у FastAPI/Uvicorn за мікросекунди, утримуючи воркери вільними. Для WebSocket з'єднань буферизація навпаки вимикається директивою `proxy_buffering off;`.
* **Обмеження частоти запитів (Rate Limiting)**: директива `limit_req_zone` захищає бекенд від шторму запитів при масовому перезавантаженні сенсорів після аварії живлення.

### 2. Спільна робота Gunicorn та UvicornWorker

У середовищі Linux прямий запуск `uvicorn app:app` не забезпечує повноцінного керування життєвим циклом процесів. Найкращою інженерною практикою є використання Gunicorn як системного супервізора процесів (Process Manager) з асинхронним класом воркера:

```bash
gunicorn fastapi_backend:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --max-requests 50000 \
    --max-requests-jitter 5000 \
    --timeout 30 \
    --graceful-timeout 10
```

Ця конфігурація забезпечує:
* **Гаряче перезавантаження без простою (Zero-Downtime Reload)**: надсилання сигналу `kill -HUP $MASTER_PID` дозволяє оновити код додатку без розриву активних клієнтських TCP-сесій.
* **Захист від витоків пам'яті (Memory Leak Mitigation)**: параметри `--max-requests` та `--max-requests-jitter` змушують Gunicorn автоматично перезапускати воркер після обробки 50 000 запитів, звільняючи фрагментовану пам'ять CPython.
* **Моніторинг завислих процесів**: якщо воркер заблокував потік або потрапив у нескінченний цикл, майстер-процес Gunicorn через `--timeout 30` примусово надсилає йому сигнал `SIGABRT` і перезапускає новий екземпляр.

## Інженерні критерії вибору фреймворку

Вибір між Flask та FastAPI визначається технічними вимогами до системи, характером навантаження та існуючою інфраструктурою проекту.

| Критерій оцінки | Flask (WSGI) | FastAPI (ASGI) |
|---|---|---|
| **Модель виконання** | Синхронна (блокування системного потоку) | Асинхронна (кооперативний цикл подій `uvloop`) |
| **Пропускна здатність I/O** | Низька (обмежена пулом потоків 10–50 req/s/thread) | Максимальна (10 000–40 000 req/s/worker) |
| **Споживання пам'яті** | Високе (стеки потоків ОС + окремі процеси) | Мінімальне (легковажні об'єкти корутин) |
| **Швидкість валідації** | Повільна (чистий Python/Marshmallow) | Ультрашвидка (скомпільоване ядро `pydantic-core` на Rust) |
| **Підтримка WebSockets / SSE** | Вимагає складних надбудов (Gevent / Flask-SocketIO) | Нативна на рівні протоколу ASGI |
| **Документація API** | Сторонні плагіни (Flasgger) з ризиком розсинхронізації | Автоматична генерація OpenAPI 3.1 та Swagger UI |
| **Впровадження залежностей** | Неявні глобальні змінні (`LocalProxy`, `request`) | Декларативний граф залежностей (`Depends`) |
| **Поріг входження** | Мінімальний (ідеальний для новачків) | Середній (вимагає розуміння `async/await` та типів) |
| **Складність кодової бази** | Проста лінійна логіка | Потребує суворого уникнення блокувального коду |

### Коли доцільно залишатися на Flask

1. **Класичні монолітні веб-додатки з серверним рендерингом**: якщо проект використовує шаблонізатор Jinja2, класичні сесії у куках та форми HTML, екосистема Flask (Flask-WTF, Flask-Login, Flask-Admin) надає готові перевірені інструменти.
2. **CPU-інтенсивні обчислювальні сервіси**: якщо обробка запиту полягає у тривалих розрахунках на процесорі (обробка зображень через OpenCV, аналіз даних у Pandas, генерація PDF) і не містить очікування мережевого I/O, асинхронний цикл подій не дає переваги перед багатопроцесним пулом Gunicorn.
3. **Legacy-інфраструктура та синхронні бібліотеки**: якщо проект жорстко зав'язаний на C-розширення чи бібліотеки баз даних, які не мають асинхронних драйверів (наприклад, старі драйвери пропрієтарних SCADA-систем чи черг повідомлень).

### Коли обов'язковим є перехід на FastAPI

1. **Шлюзи збору телеметрії IoT та мікросервісні API**: при необхідності одночасно утримувати з'єднання з тисячами сенсорів, шлюзів чи мікросервісів за мінімальних витрат пам'яті.
2. **Робота з асинхронними сховищами даних**: при використанні сучасних асинхронних драйверів (PostgreSQL через `asyncpg`, MongoDB через `motor`, Redis через `redis-py` async, Kafka/RabbitMQ через `aiokafka`/`aio-pika`).
3. **Протоколи реального часу (WebSockets, SSE)**: для організації двонаправлених каналів зв'язку з IoT-контролерами або живої трансляції показників на дашборди моніторингу.
4. **Суворі вимоги до надійності даних та типізації**: у проектах, де некоректний формат числа від датчика може спричинити збій у системі управління, апаратна строгість валідації Pydantic запобігає проникненню «брудних» даних на рівні мережевого шлюзу.
5. **Командна розробка та генерація клієнтських бібліотек**: коли API використовується сторонніми клієнтами, і наявність актуальної OpenAPI-специфікації є обов'язковою умовою інтеграції.
