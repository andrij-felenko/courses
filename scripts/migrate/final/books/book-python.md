# Довідник «Python»

**Слуг:** `python` · **Вид:** `reference/` · **Тека:** `reference/python/` · **Назва:** Python

**Опис.** Довідник мови Python і того, що навколо неї: модель даних, функції й класи,
інтерпретатор CPython і його ціна, підказки типів, стандартна бібліотека в тій частині,
яку справді відкривають, файли й формати, бінарні дані й послідовний порт, мережа,
паралельність, тестування, пакування, MicroPython на мікроконтролері — і окремо ті місця,
де код робить не те, що очевидно з тексту.

**Чому довідник, а не книга.** Питання «а в якій версії?» доречне на кожній сторінці:
`match` є з 3.10, `except*` з 3.11, збірка без GIL з 3.13, `dict` упорядкований з 3.7.
Мова — рукотворна система з релізами й PEP-ами, тож `reference/`. Сусід по полиці —
`reference/cpp-standards`.

**Межа з `book/programming`.** Принцип лежить у книзі, втілення — тут, і вони лінкують
одне одного: `book:programming/garbage-collection` ↔ `book:python/refcount-and-cycle-gc`,
`book:programming/async-await` ↔ `book:python/coroutines-and-await`,
`book:programming/global-interpreter-lock` ↔ `book:python/cpython-gil`,
`book:programming/socket-api` ↔ `book:python/socket-module`,
`book:programming/json-format` ↔ `book:python/json-module`,
`book:programming/dependency-management` ↔ `book:python/lock-files`.
Довідник **не переказує** принцип — він показує, як саме ця мова його реалізувала і чим
за це платить.

**Обсяг:** 14 розділів, 219 тем.

---

## Як влаштовані розділи

Розділ тут — **етап роботи або природа проблеми**, а не полиця предмета. Тому немає
розділу «стандартна бібліотека»: `pathlib` лежить біля кодувань, `struct` — біля
послідовного порту, `logging` — біля трейсбека й профайлера, бо саме так вони й
відкриваються. І тому є розділ «Пастки»: людина, у якої скрипт мовчки з'їв виняток або
підмінив модуль своїм файлом, шукає не «замикання», а «чому воно так».

Порядок розділів — від того, що мусиш розуміти в будь-якому рядку, до того, що
відкриваєш, коли річ уже написана. Але це довідник: кожна тема — самодостатній атом і
читається окремо.

---

## 1. `objects` — Об'єкти й типи

*Що таке значення в Python, як ім'я з ним пов'язане і які типи мова дає з коробки.*
**21 тема**

| слуг | назва |
|---|---|
| `everything-is-object` | Усе є об'єктом |
| `names-and-binding` | Імена, прив'язка й посилання |
| `mutable-and-immutable` | Змінювані й незмінні об'єкти |
| `is-operator` | Оператор is і тотожність об'єктів |
| `hashable-objects` | Хешовність об'єкта |
| `truthiness` | Істинність об'єкта |
| `int-arbitrary-precision` | Ціле необмеженої розрядності |
| `float-precision` | float і межі його точності |
| `str-unicode-model` | Рядок як послідовність код-пойнтів |
| `string-formatting` | f-рядки й специфікатори формату |
| `bytes-and-memoryview` | bytes, bytearray і memoryview |
| `list-type` | Список і ціна його операцій |
| `tuple-type` | Кортеж і розпакування |
| `dict-type` | Словник і його впорядкованість |
| `set-type` | Множини set і frozenset |
| `slicing` | Зрізи й від'ємні індекси |
| `sorting-with-key` | Сортування з key і стабільність |
| `copy-module` | Поверхнева й глибока копія |
| `collections-module` | Контейнери з collections |
| `datetime-and-timezones` | Дата, час і часові пояси |
| `numeric-arrays` | Масиви чисел array і numpy |

## 2. `control-flow` — Потік виконання й винятки

*Як виконується код і що відбувається, коли він відмовляється виконуватися далі.*
**16 тем**

| слуг | назва |
|---|---|
| `loops-and-else` | Цикли, break і else при циклі |
| `iteration-protocol` | Протокол ітерації |
| `range-enumerate-zip` | range, enumerate і zip |
| `comprehensions` | Спискові, словникові й множинні включення |
| `unpacking-and-star` | Розпакування й зірочка |
| `raising-and-catching` | Підняття й перехоплення винятків |
| `exception-hierarchy` | Ієрархія вбудованих винятків |
| `custom-exceptions` | Власні класи винятків |
| `finally-and-cleanup` | finally й гарантоване прибирання |
| `exception-chaining` | Ланцюг винятків і raise from |
| `exception-groups` | Групи винятків і except* |
| `context-managers` | Менеджери контексту й with |
| `contextlib` | Контекст із генератора |
| `match-statement` | match і зіставлення зі зразком |
| `assert-statement` | assert і прапорець -O |
| `eafp-vs-lbyl` | EAFP і LBYL |

## 3. `functions` — Функції й генератори

*Як оголошується виклик, що він захоплює з собою і як одна функція перетворює іншу.*
**16 тем**

| слуг | назва |
|---|---|
| `function-definition` | Означення функції та її об'єкт |
| `arguments-and-defaults` | Аргументи й значення за замовчуванням |
| `star-args-kwargs` | *args і **kwargs |
| `positional-only-keyword-only` | Позиційні-лише й іменовані-лише параметри |
| `scopes-legb` | Області видимості, global і nonlocal |
| `closure-cells` | Замикання й комірки |
| `lambda-expression` | lambda і межі виразу |
| `decorators` | Декоратори |
| `decorators-with-arguments` | Декоратори з аргументами й functools.wraps |
| `functools-partial` | partial і зафіксовані аргументи |
| `lru-cache` | Кешування виклику |
| `generators` | Генератори й yield |
| `generator-send-close` | send, throw і закриття генератора |
| `yield-from` | yield from і делегування |
| `genexpr` | Генераторні вирази й лінива обробка |
| `recursion-limit` | Рекурсія й межа глибини |

## 4. `classes` — Класи й об'єктна модель

*Як з'являється власний тип, що при цьому робить інтерпретатор і скільки з цього справді
потрібно.* **17 тем**

| слуг | назва |
|---|---|
| `class-definition` | Оголошення класу й простір його імен |
| `instance-vs-class-attributes` | Атрибути примірника й атрибути класу |
| `init-and-new` | \_\_init\_\_ і \_\_new\_\_ |
| `classmethod-staticmethod` | classmethod і staticmethod |
| `dunder-protocols` | Дандер-методи як протоколи мови |
| `repr-and-str` | \_\_repr\_\_ і \_\_str\_\_ |
| `property-decorator` | Властивість замість гетера |
| `descriptor-protocol` | Протокол дескриптора |
| `dunder-slots` | \_\_slots\_\_ і розмір примірника |
| `inheritance-and-mro` | Спадкування й порядок розв'язання методів |
| `super-call` | super() і кооперативний виклик |
| `abstract-base-classes` | Абстрактні базові класи |
| `duck-typing` | Качина типізація |
| `dataclasses` | Класи-дані |
| `enum-classes` | Enum, IntEnum і Flag |
| `metaclasses` | Метакласи |
| `dynamic-attributes` | \_\_getattr\_\_ і динамічні атрибути |

## 5. `typing` — Підказки типів

*Анотації, яких інтерпретатор не перевіряє, і те, що з ними роблять перевіряч і
бібліотеки.* **12 тем**

| слуг | назва |
|---|---|
| `annotations-basics` | Анотації і що з ними робить рантайм |
| `builtin-generics` | Узагальнення вбудованих типів |
| `optional-and-union` | Optional, Union і оператор \| |
| `special-types` | Any, object і Never |
| `typing-protocol` | Protocol і структурна типізація |
| `typevar-and-generics` | TypeVar і власні узагальнені типи |
| `callable-and-paramspec` | Callable і ParamSpec |
| `typeddict-and-literal` | TypedDict, Literal і NewType |
| `mypy-checking` | Перевірка типів mypy |
| `gradual-typing` | Поступова типізація наявного коду |
| `runtime-annotations` | Анотації під час виконання |
| `pydantic-validation` | Валідація даних за анотаціями |

## 6. `interpreter` — Інтерпретатор CPython

*Що насправді робить CPython, виконуючи код, і чим Python платить за свою зручність.*
**15 тем**

| слуг | назва |
|---|---|
| `cpython-execution-model` | Шлях від тексту до байткоду |
| `bytecode-and-dis` | Байткод і модуль dis |
| `object-layout` | Устрій об'єкта в пам'яті |
| `refcount-and-cycle-gc` | Підрахунок посилань і збирач циклів |
| `pymalloc-arenas` | Аллокатор pymalloc і повернення пам'яті |
| `cpython-gil` | GIL у CPython |
| `free-threaded-python` | Збірка без GIL |
| `interpreter-startup` | Запуск інтерпретатора й час старту |
| `attribute-lookup` | Ціна пошуку атрибута |
| `performance-model` | Чому Python повільний і де саме |
| `adaptive-interpreter-jit` | Спеціалізація й JIT у сучасному CPython |
| `c-extensions` | Розширення на C і Python/C API |
| `ctypes-and-cffi` | ctypes і cffi |
| `alternative-implementations` | PyPy, GraalPy та інші реалізації |
| `python-versions-eol` | Версії Python, сумісність і кінець підтримки |

## 7. `files` — Файли й формати

*Читання й записування того, що лежить на диску: шляхи, кодування, текстові й табличні
формати, локальна база.* **20 тем**

| слуг | назва |
|---|---|
| `open-and-file-objects` | open, режими й файловий об'єкт |
| `text-vs-binary-mode` | Текстовий і бінарний режим |
| `encodings-and-utf8` | Кодування, UTF-8 і помилки декодування |
| `pathlib` | Шлях як об'єкт |
| `directory-walking` | Обхід дерева каталогів |
| `temp-files` | Тимчасові файли й каталоги |
| `atomic-write` | Атомний запис і збереження на диск |
| `shutil-operations` | Копіювання, переміщення й видалення дерев |
| `large-file-streaming` | Читання великого файлу потоком |
| `json-module` | Модуль json |
| `json-custom-types` | Власні типи в JSON |
| `csv-module` | CSV, діалекти й заголовок |
| `toml-and-ini` | Конфігураційні формати TOML та INI |
| `yaml-safety` | YAML і безпечне завантаження |
| `pickle-danger` | pickle і його небезпека |
| `sqlite3-module` | Локальна база sqlite3 |
| `archives-zip-tar` | Архіви zip і tar |
| `regex-module` | Регулярні вирази |
| `xml-parsing` | Розбір XML з ElementTree |
| `tabular-analysis` | Таблиці й графіки для аналізу даних |

## 8. `binary` — Бінарні дані й послідовний порт

*Байти, а не текст: як зібрати й розібрати пакет і як говорити з пристроєм на дроті.*
**13 тем**

| слуг | назва |
|---|---|
| `struct-module` | struct і пакування чисел у байти |
| `endianness-in-struct` | Порядок байтів і вирівнювання у struct |
| `bit-operations` | Бітові операції над цілими |
| `int-bytes-conversion` | to_bytes і from_bytes |
| `frame-parsing` | Кадрування байтового потоку |
| `checksums-crc` | Контрольні суми й CRC |
| `pyserial-basics` | pyserial і параметри порту |
| `serial-timeouts` | Таймаути й неповні кадри на порту |
| `serial-port-discovery` | Пошук потрібного порту |
| `pymavlink` | pymavlink і діалекти MAVLink |
| `telemetry-log-parsing` | Розбір журналів телеметрії |
| `linux-gpio-i2c-spi` | GPIO, I²C і SPI з Python на одноплатнику |
| `python-can` | CAN-шина з python-can |

## 9. `network` — Мережа й HTTP

*Як скрипт розмовляє з іншою машиною: сокет, HTTP-клієнт, простий сервіс і черга
повідомлень.* **14 тем**

| слуг | назва |
|---|---|
| `socket-module` | Модуль socket і TCP-з'єднання |
| `udp-datagrams` | UDP-датаграми й втрати |
| `socket-timeouts` | Таймаути й неблокувальний сокет |
| `requests-client` | HTTP-клієнт requests |
| `sessions-and-pooling` | Сесія, пул з'єднань і keep-alive |
| `retries-and-backoff` | Повтори й експоненційна витримка |
| `auth-tokens` | Токени й заголовки автентифікації |
| `tls-certificates` | TLS і перевірка сертифікатів |
| `streaming-bodies` | Потокове передавання великих тіл |
| `http-server-minimal` | Найпростіший HTTP-сервер |
| `flask-and-fastapi` | Flask і FastAPI |
| `websockets-python` | WebSocket-клієнт і сервер |
| `mqtt-paho` | MQTT з paho-mqtt |
| `url-parsing` | Розбір URL і кодування параметрів |

## 10. `concurrency` — Паралельність і асинхронність

*Чотири різні способи робити кілька справ водночас — і чому в Python вибір між ними не
косметичний.* **16 тем**

| слуг | назва |
|---|---|
| `threading-basics` | Потоки в threading |
| `when-threads-help` | Коли потоки прискорюють, а коли ні |
| `locks-and-conditions` | Замки, RLock і умовні змінні |
| `queue-module` | Черга між потоками |
| `concurrent-futures` | Пули в concurrent.futures |
| `multiprocessing-module` | Процеси замість потоків |
| `ipc-between-processes` | Обмін даними між процесами |
| `asyncio-event-loop` | Цикл подій asyncio |
| `coroutines-and-await` | Корутини й await |
| `tasks-and-taskgroup` | Задачі, gather і TaskGroup |
| `asyncio-cancellation` | Скасування задач і таймаути |
| `blocking-in-async` | Блокувальний виклик у циклі подій |
| `asyncio-streams` | Асинхронні сокети й сервери |
| `subprocess-module` | Запуск чужої програми |
| `subprocess-pipes` | Труби, буфери й затики |
| `signals-and-shutdown` | Сигнали й коректне завершення |

## 11. `micropython` — MicroPython і CircuitPython

*Той самий синтаксис на мікроконтролері — і все, що там працює інакше або не працює
зовсім.* **14 тем**

| слуг | назва |
|---|---|
| `micropython-overview` | Що таке MicroPython |
| `micropython-vs-cpython` | Чим MicroPython відрізняється від CPython |
| `micropython-memory` | Пам'ять і купа на мікроконтролері |
| `micropython-gc-pauses` | Збирач сміття й паузи |
| `micropython-repl-flashing` | REPL, прошивання й файли на платі |
| `micropython-machine-module` | Піни, АЦП і ШІМ у модулі machine |
| `micropython-buses` | I²C, SPI і UART у MicroPython |
| `micropython-interrupts` | Переривання й обробники |
| `micropython-ticks` | Час, затримки й переповнення ticks |
| `micropython-network` | Мережа на ESP32 |
| `micropython-asyncio` | Асинхронність на мікроконтролері |
| `micropython-power` | Сон і споживання |
| `circuitpython` | CircuitPython і його модель |
| `micropython-limits` | Де MicroPython не годиться |

## 12. `testing` — Тестування й налагодження

*Як переконатися, що скрипт робить обіцяне, і як з'ясувати, чому не робить.* **16 тем**

| слуг | назва |
|---|---|
| `pytest-basics` | Тест як звичайна функція |
| `pytest-fixtures` | Фікстури й області їхньої дії |
| `pytest-parametrize` | Параметризовані тести |
| `mock-and-patch` | Мок і підміна залежності |
| `fake-hardware-in-tests` | Фейковий порт і фейковий пристрій |
| `test-isolation` | Ізоляція тесту від середовища |
| `testing-async-code` | Тестування асинхронного коду |
| `coverage-measurement` | Покриття коду й що воно не міряє |
| `hypothesis-testing` | Тестування властивостями |
| `tests-in-ci` | Розкладка тестів і запуск у CI |
| `logging-module` | Модуль logging |
| `traceback-reading` | Читання трейсбека |
| `pdb-debugger` | Відлагоджувач pdb |
| `profiling-cprofile` | Профілювання cProfile і timeit |
| `tracemalloc-leaks` | tracemalloc і витік пам'яті |
| `hang-diagnosis` | Діагностика зависання |

## 13. `packaging` — Модулі, пакети й середовища

*Як код стає імпортовним, встановлюваним і відтворюваним на чужій машині.* **18 тем**

| слуг | назва |
|---|---|
| `module-object` | Модуль як об'єкт |
| `import-machinery` | Механіка імпорту |
| `sys-path` | sys.path і звідки він береться |
| `packages-and-init` | Пакети й \_\_init\_\_.py |
| `relative-imports` | Відносні імпорти |
| `circular-imports` | Циклічні імпорти |
| `main-and-dash-m` | \_\_main\_\_, -m і точка входу |
| `venv` | Віртуальне середовище |
| `pip-install` | pip і джерела пакетів |
| `requirements-pinning` | requirements.txt і закріплення версій |
| `pyproject-toml` | Метадані проєкту в pyproject.toml |
| `wheels-and-sdist` | sdist, wheel і бінарні колеса |
| `dependency-conflicts` | Конфлікти версій залежностей |
| `lock-files` | Замки залежностей і сучасні менеджери |
| `linters-and-formatters` | Лінтер і форматувальник у проєкті |
| `pyinstaller-freeze` | Заморожування застосунку в один файл |
| `python-on-device` | Python на цільовому пристрої |
| `system-python` | Системний Python і чому його не чіпають |

## 14. `pitfalls` — Пастки

*Місця, де код робить не те, що очевидно з тексту, і де інтуїція з C систематично бреше.*
**11 тем**

| слуг | назва |
|---|---|
| `mutable-default-argument` | Змінюваний аргумент за замовчуванням |
| `late-binding-in-loops` | Пізнє зв'язування замикань у циклі |
| `mutating-while-iterating` | Зміна колекції під час обходу |
| `float-equality` | Порівняння дробових чисел |
| `interning-and-caching` | Кешування малих цілих і інтернування рядків |
| `shadowing-stdlib-modules` | Файл з іменем стандартного модуля |
| `broad-except` | Перехоплення всіх винятків |
| `atomicity-and-races` | Що атомарне, а що ні |
| `shell-injection-subprocess` | shell=True і лапки в аргументах |
| `naive-datetime` | Наївний час без пояса |
| `eval-untrusted-input` | eval, exec і чужі дані |

---

# Що з цього потрібне курсу embedded

Курс просить Python у чотирьох місцях, і жодного разу його не вчить. Нижче — що саме
кожне з цих місць потребує.

> **Про нумерацію.** У чинному плані томів їх **14**, не 15. У завданні названо томи
> 3, 10, 12, 15 — читаю це як: **3 «Мікроконтролери»** (автоматизація тестування),
> **10 «Архітектура IoT»** (серверна частина), **12 «Автоматизація і пряме керування»**
> (наземна станція), **14 «Продукт»** (тестування, CI, постачання прошивки). Саме там
> ці кроки й лежать за розкладками `vols2/vol-embedded-03|10|12|14.md`.

## Том 3 «Мікроконтролери» — автоматизація тестування

**Просить уже зараз:** модуль 15 «Інженерія якості прошивки» → кроки `Python для
автоматизації тестування` (ref у `book/programming/software-engineering`), `SITL`,
`Модульний тест`, `Тестування прошивки`. Це **найраніша** точка, де курс уперше вимагає
мови хоста — отже саме тут і мусить стояти вхід у Python.

**Мінімальний набір (26 тем).** Мова: `everything-is-object`, `names-and-binding`,
`mutable-and-immutable`, `truthiness`, `list-type`, `dict-type`, `tuple-type`,
`str-unicode-model`, `string-formatting`, `loops-and-else`, `comprehensions`,
`iteration-protocol`, `raising-and-catching`, `context-managers`, `function-definition`,
`arguments-and-defaults`, `scopes-legb`. Робота: `pytest-basics`, `pytest-fixtures`,
`pytest-parametrize`, `mock-and-patch`, `fake-hardware-in-tests`, `test-isolation`,
`subprocess-module`, `pathlib`, `venv`.

**Чому саме тут.** Тестова автоматизація прошивки — це запустити чужу програму
(`subprocess-module`), поговорити з платою через порт (`pyserial-basics`,
`serial-timeouts` — можна віддати в том 4 разом із UART) і сказати «очікую ось це»
(`pytest-basics`). Без `mutable-and-immutable` і `names-and-binding` читач із C напише
тест, що ділить стан між прогонами, і не зрозуміє чому.

## Том 10 «Архітектура IoT» — серверна частина

**Просить уже зараз:** `Веб-сервер на МК`, `Серверна частина OTA`, `Телеметрія`,
плюс дві діри, які розкладка тому назвала прямо: «немає жодної мови для хоста» і
«сховище даних як предмет відсутнє повністю».

**Потрібне (34 теми).** Мережа: `socket-module`, `udp-datagrams`, `socket-timeouts`,
`requests-client`, `sessions-and-pooling`, `retries-and-backoff`, `auth-tokens`,
`tls-certificates`, `streaming-bodies`, `http-server-minimal`, `flask-and-fastapi`,
`websockets-python`, `mqtt-paho`, `url-parsing`. Дані: `json-module`,
`json-custom-types`, `sqlite3-module`, `csv-module`, `toml-and-ini`,
`datetime-and-timezones`, `naive-datetime`, `pydantic-validation`. Одночасність:
`asyncio-event-loop`, `coroutines-and-await`, `tasks-and-taskgroup`,
`asyncio-cancellation`, `blocking-in-async`, `asyncio-streams`, `queue-module`,
`when-threads-help`, `cpython-gil`. Експлуатація: `logging-module`, `python-on-device`,
`signals-and-shutdown`.

**Найважче тут — не синтаксис, а `cpython-gil` + `when-threads-help` + `blocking-in-async`.**
Приймач телеметрії, написаний людиною з досвіду C, майже завжди виявляється або
однопотоковим із заблокованим циклом подій, або багатопотоковим без прискорення. Ці три
теми — причина, з якої розділ узагалі потрібен.

## Том 12 «Автоматизація і пряме керування» — наземна станція

**Просить уже зараз:** модуль 27 «Канал керування й зв'язок із землею» → власні кроки
`Python для наземних скриптів`, `pymavlink`, `MAVLink із землі`; модуль 29 «Наземна
станція: QGroundControl» → `Запис і відтворення телеметрії`; `Генерація коду з XML
MAVLink`.

**Потрібне (18 тем).** `pymavlink`, `telemetry-log-parsing`, `struct-module`,
`endianness-in-struct`, `frame-parsing`, `checksums-crc`, `bit-operations`,
`int-bytes-conversion`, `bytes-and-memoryview`, `pyserial-basics`, `serial-timeouts`,
`serial-port-discovery`, `udp-datagrams`, `xml-parsing`, `numeric-arrays`,
`tabular-analysis`, `enum-classes`, `dataclasses`.

**Дві звірки з наявним курсом.**
1. Крок `guide/embedded` `pymavlink` (модуль 27) уже написаний і `done` — і слуг у мене
   збігається. Це та сама «одна тема двічі» з §1: атом у довіднику, кумулятивний крок у
   курсі. Рішення людське, і воно одне з двох: або лишити обидва (тоді крок курсу лінкує
   атом), або перевести крок у `ref:"python/binary/pymavlink"`. Мовчки не зливати.
2. `Генерація коду з XML MAVLink` спирається на `xml-parsing` — цієї передумови в курсі
   немає ніде.

## Том 14 «Продукт» — тестування, CI, постачання

**Просить уже зараз:** `CI для прошивки`, `Статичний аналіз`, `HIL-стенд`, `SITL`,
`Python для автоматизації тестування`, `Заводське прошивання й провізіонування`,
`OTA-оновлення`, `Тест-джиг` (модуль 34).

**Потрібне (16 тем).** `tests-in-ci`, `coverage-measurement`, `hypothesis-testing`,
`testing-async-code`, `linters-and-formatters`, `mypy-checking`, `gradual-typing`,
`pyproject-toml`, `requirements-pinning`, `lock-files`, `dependency-conflicts`,
`wheels-and-sdist`, `pyinstaller-freeze`, `system-python`, `python-versions-eol`,
`atomic-write`.

**Чому `pyinstaller-freeze` і `system-python` саме тут.** Стенд провізіонування стоїть у
цеху, а не в майстерні автора: там немає мережі, немає pip і немає права ставити пакети
в системний Python. `atomic-write` — бо скрипт провізіонування пише серійники й ключі, і
обірване живлення на середині запису псує партію.

## Дві теми, яких у мене свідомо немає, а курсу вони потрібні

- **«Python за годину для того, хто знає C»** (кандидат курсу) — вхід, який спирається на
  вже відоме й порівнює з пройденим. За залізним правилом §1 це `guide`, ніколи `book`
  чи `reference`. **Адреса: власна стаття курсу `guide/embedded`, том 3**, що ref-иться
  на атоми розділів 1–3 цього довідника.
- **«Огляд екосистеми для інженера»** — які бібліотеки беруть у польових задачах і чому.
  Це теж курсовий кут (вибір під конкретну задачу тому), а не атом. **Адреса: том 10.**

---

# Чого свідомо не беремо

**Веб-розробка як фах.** Django, шаблонізатори, ORM, автентифікація сесіями, черги
Celery. Корпусу потрібен HTTP-**клієнт** і мінімальний сервіс для IoT — це `requests-client`
і `flask-and-fastapi`, два атоми. Архітектура бекенду вже описана в
`book/programming/web-backend` (43 теми) і мовою не пахне.

**Наука про дані.** pandas углиб, scikit-learn, Jupyter як середовище, візуалізація як
дисципліна. Лишаю один атом `tabular-analysis` — рівно стільки, щоб побудувати графік
з логу польоту. Далі це інша галузь і, ймовірно, інша книга.

**GUI.** tkinter, PySide/PyQt, kivy. Qt/QML — **свідомо поза корпусом назавжди**
(правило CLAUDE.md), а tkinter не потрібен жодному тому: наземна станція курсу — це
QGroundControl, і вона має власний довідник.

**ORM і SQLAlchemy.** Робота з базою як дисципліна лежить у `book/programming/databases`
(29 тем). Тут потрібен `sqlite3-module` — файл поруч зі скриптом, який переживе
перезавантаження шлюзу.

**Альтернативні асинхронні каркаси.** Twisted, Tornado, Trio, gevent. Історично цікаво,
практично корпус живе на `asyncio`. Місце для згадки — `hist-`-вставка при
`asyncio-event-loop`.

**Прискорювачі окремими темами.** Cython, Numba, Nuitka, mypyc. Одна тема
`performance-model` називає їх і каже, коли який доречний; окремі статті про кожен —
це вже інша книга. Так само `subinterpreters` (PEP 734) і `__future__` — вставки при
`free-threaded-python` і `python-versions-eol`.

**Перевірячі типів, крім mypy.** pyright, pytype, pyre. Один атом `mypy-checking`
описує механіку, а не продукт; відмінності — вставкою.

**Менеджери залежностей окремими темами.** poetry, pdm, uv, pipenv, conda. Один атом
`lock-files` про **замок і розв'язання версій**; імена інструментів у ньому. Ставити
статтю на кожен — це каталог, а не довідник, і він застаріє за рік.

**Історія Python 2 → 3.** Не розділ і не тема: `hist-`-вставка при `python-versions-eol`.
Читачеві корпусу трапиться хіба чужий скрипт, і йому потрібен не переказ переходу, а
ознака, за якою він упізнає код із того боку.

**Синтаксична дрібнота.** Значущі відступи, `print`, арифметичні оператори, `if/else`,
іменування за PEP 8. Читач цього корпусу пише на C — це не атоми, а рядок у сусідній
статті. Тому в розділі 2 немає теми «оператори й блоки».

**Плати, на яких біжить MicroPython.** ESP32, RP2040, Pico W як **вироби** — це
`catalog/boards`, річ, яку можна купити. Довідник описує MicroPython, а не залізо під ним.

**Те, що вже є атомом у `book/programming`.** Збирання сміття як принцип, async/await як
ідея, API сокетів, JSON як формат, керування залежностями як дисципліна, GIL як поняття,
статична й динамічна типізація, замикання, підрахунок посилань. Довідник описує
**втілення саме в Python** і лінкує в книгу; переказувати принцип ще раз заборонено §1.

---

# Технічні примітки для того, хто заводитиме маніфест

**Реєстрація.** `reference/python/manifest.js` пушить у той самий `window.__BOOKS__` з
`type:"reference"`; слуг `python` додати в `REFERENCE_BOOKS` у `books-index.js`.
Дефолт кожної теми — `basic:{status:"empty"}`, `detailed:{status:"pending"}` (§3).

**Очікувані попередження «⚠ МОЖЛИВІ ДУБЛІ ПОНЯТЬ» від `manifest-patch.js`** — перевірено
проти всіх 5330 слугів корпусу. Це не помилки, а свідомі рішення:

| мій слуг | зачепить | чому лишаю |
|---|---|---|
| `pymavlink` | `guide/embedded` (власний крок, `done`) | та сама тема двічі, §1 — див. звірку тому 12 |
| `mqtt-paho` | `communications/mqtt` | там протокол, тут бібліотека |
| `tls-certificates` | `security/tls` | там криптографія, тут `ssl` і перевірка ланцюга |
| `linux-gpio-i2c-spi` | `electronics/gpio`, `i2c` | там шина, тут `gpiod`/`smbus` на хості |
| `checksums-crc` | `communications/crc` | там поліном, тут `zlib.crc32` і таблиці |
| `asyncio-event-loop` | `programming/event-loop` | там патерн, тут `asyncio` |
| `micropython-interrupts`, `micropython-power` | `interrupts`, `power` | префікс навмисний |

**Перейменовано під час проєктування, щоб уникнути глухого дубля:**
`generator-expressions` → **`genexpr`** (у `reference/build-systems` цим слугом названо
генераторні вирази CMake — інше поняття тими самими словами); `properties` →
**`property-decorator`**; `descriptors` → **`descriptor-protocol`**; `slots` →
**`dunder-slots`**.

**Про мову коду (§5).** Правило «є C — має бути й C++» до цієї книги не застосовується:
приклади тут мовою Python. Вкладки `:::tabs` доречні там, де сенс саме в порівнянні —
`micropython-vs-cpython` (CPython ↔ MicroPython), `ctypes-and-cffi` і `c-extensions`
(Python ↔ C-сторона), `mypy-checking` (до/після анотацій).

**Кандидат на `_canon.md`.** Наскрізний приклад книги напрошується один — **скрипт, що
читає телеметрію з порту, розбирає кадр і кладе в базу**: він проходить крізь розділи 7,
8, 9, 10 і 12 і дає темам спільний словник. Рішення за автором; без файлу пишеться за
загальним каноном.
