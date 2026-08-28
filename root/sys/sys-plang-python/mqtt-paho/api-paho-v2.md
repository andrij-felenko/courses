# 📋 Інтерфейс клієнта paho-mqtt версії 2.x

Бібліотека `paho-mqtt` є офіційною еталонною реалізацією клієнта протоколів MQTT версій 3.1, 3.1.1 та 5.0 для мови Python під егідою Eclipse Foundation. Починаючи з мажорного релізу `paho-mqtt 2.0.0`, інтерфейс клієнта зазнав фундаментальної переробки з метою усунення застарілого технічного боргу, надійного розділення версій сигнатур та забезпечення повноцінної типізованої підтримки розширених можливостей стандарту MQTT 5.0.

У версії 2.x обов'язковою вимогою є явна передача версії API зворотних викликів (`CallbackAPIVersion`) під час ініціалізації екземпляра клієнта. Спроба створити клієнт через `Client()` без зазначення параметра викликає виняток `ValueError`.

Нижче наведено вичерпну довідку публічного API клієнта `paho.mqtt.client.Client` для версії API `CallbackAPIVersion.VERSION2`.

## 1. Ініціалізація та налаштування клієнта

Клас `Client` інкапсулює стан мережевого TCP-з'єднання, внутрішні черги відправлення, буфери вхідних пакетів, лічильники транзакцій та механізм диспетчеризації зворотних викликів.

```python
class paho.mqtt.client.Client(
    callback_api_version: CallbackAPIVersion,
    client_id: str = "",
    clean_session: bool | None = None,
    userdata: Any = None,
    protocol: int = MQTTv311,
    transport: str = "tcp",
    reconnect_on_failure: bool = True,
    manual_ack: bool = False
)
```

### Параметри конструктора

- `callback_api_version` (`CallbackAPIVersion`): обов'язковий перелік, що визначає сигнатуру виклику всіх зареєстрованих обробників подій. Для нового коду слід завжди передавати `CallbackAPIVersion.VERSION2`. Значення `CallbackAPIVersion.VERSION1` залишене виключно для тимчасової зворотної сумісності зі старими кодовими базами.
- `client_id` (`str`): унікальний ідентифікатор клієнта (Client Identifier) на брокері. Відповідно до стандарту MQTT, довжина рядка зазвичай становить від 1 до 23 символів (у MQTT 5.0 обмеження знято). Якщо передано порожній рядок `""`, брокер автоматично згенерує унікальний випадковий ідентифікатор (вимагає прапорця `clean_session=True` або `clean_start=True`).
- `clean_session` (`bool | None`): прапорець очищення сесії для протоколу MQTT 3.1.1. Якщо встановлено `True`, брокер знищує всі підписки та непідтверджені черги повідомлень після відключення клієнта. Якщо `False`, брокер зберігає стан сесії (Persistent Session). Для MQTT 5.0 цей параметр не використовується і замінений на `clean_start` у методі `connect()`.
- `userdata` (`Any`): довільний об'єкт (екземпляр користувацького класу, словник стану, черга `queue.Queue` або пул з'єднань), який автоматично передається другим аргументом у всі функції зворотного виклику. Дозволяє повністю уникнути використання глобальних змінних.
- `protocol` (`int`): версія протоколу зв'язку. Допустимі константи: `paho.mqtt.client.MQTTv31` (MQTT 3.1), `paho.mqtt.client.MQTTv311` (MQTT 3.1.1, за замовчуванням), `paho.mqtt.client.MQTTv5` (MQTT 5.0).
- `transport` (`str`): тип мережевого транспорту. Допустимі значення: `"tcp"` (стандартний прямий TCP-сокет) або `"websockets"` (інтерфейс поверх протоколу WebSocket, що використовується для взаємодії через HTTP-проксі та фаєрволи).
- `reconnect_on_failure` (`bool`): якщо `True` (за замовчуванням), клієнт автоматично переходить у стан повторного підключення при раптовому обриві сокета під час роботи у фонових циклах `loop_start()` та `loop_forever()`.
- `manual_ack` (`bool`): якщо встановлено `True`, клієнт вимикає автоматичне надсилання пакетів підтвердження `PUBACK` (для QoS 1) та `PUBREC`/`PUBCOMP` (для QoS 2). Розробник отримує змогу самостійно підтверджувати отримані повідомлення після їхньої фактичної обробки та збереження.

## 2. Сигнатури зворотних викликів у VERSION2

У версії `CallbackAPIVersion.VERSION2` сигнатури функцій стандартизовано для одночасної роботи з протоколами MQTT 3.1.1 та MQTT 5.0. Замість застарілого цілого числа `rc` усі методи отримують типізовані екземпляри `ReasonCode` та опціональні об'єкти розширених властивостей `Properties`.

### Зворотний виклик `on_connect`

Викликається після успішного встановлення TCP-з'єднання та отримання від брокера пакета підтвердження `CONNACK`.

```python
def on_connect(
    client: Client,
    userdata: Any,
    flags: ConnectFlags,
    reason_code: ReasonCode,
    properties: Properties | None
) -> None
```

- `flags` (`ConnectFlags`): об'єкт із прапорцями підключення. Поле `flags.session_present` (`bool`) сигналізує, чи зберіг брокер стан попередньої сесії клієнта. Якщо `session_present == False`, клієнт зобов'язаний повторно надіслати підписки на топіки.
- `reason_code` (`ReasonCode`): об'єкт результату підключення. Успішне з'єднання відповідає умові `not reason_code.is_failure` або числовому значенню `0` (`Success`). При відмові повертає конкретну причину (наприклад, `NotAuthorized`, `BadUserNameOrPassword`, `ServerUnavailable`, `ServerBusy`, `QuotaExceeded`).
- `properties` (`Properties | None`): властивості пакета `CONNACK` стандарту MQTT 5.0, надіслані брокером (наприклад, `ReceiveMaximum`, `MaximumPacketSize`, `TopicAliasMaximum`, `UserProperty`).

### Зворотний виклик `on_disconnect`

Викликається при розриві мережевого з'єднання, вичерпанні таймауту Keep-Alive або після явного виклику методу `client.disconnect()`.

```python
def on_disconnect(
    client: Client,
    userdata: Any,
    disconnect_flags: DisconnectFlags,
    reason_code: ReasonCode,
    properties: Properties | None
) -> None
```

- `disconnect_flags` (`DisconnectFlags`): контекстні прапорці розриву (вказують, чи було відключення ініційоване локальним додатком).
- `reason_code` (`ReasonCode`): статус розриву. Значення `0` (`Success`) вказує на коректне вимкнення за ініціативою клієнта. Будь-яке інше значення вказує на мережевий збій, таймаут пінгу або ініційоване брокером відключення (наприклад, `SessionTakenOver`, `KeepAliveTimeout`, `AdministrativeAction`).

### Зворотний виклик `on_message`

Викликається щоразу, коли з мережевого сокета вичитано та декодовано вхідний пакет `PUBLISH` за однією з оформлених підписок.

```python
def on_message(
    client: Client,
    userdata: Any,
    message: MQTTMessage
) -> None
```

Об'єкт `message` (`MQTTMessage`) містить такі публічні атрибути:
- `message.topic` (`str`): назва топіка, в який надійшло повідомлення.
- `message.payload` (`bytes`): сирі бінарні дані повідомлення.
- `message.qos` (`int`): рівень гарантії доставки (`0`, `1` або `2`).
- `message.retain` (`bool`): прапорець збереженого повідомлення (`Retained`). Якщо `True`, повідомлення було збережене на брокері та надіслане клієнту відразу після підписки як останній актуальний стан.
- `message.mid` (`int`): порядковий числовий номер пакета (Message ID) у сесії для повідомлень з QoS 1 та QoS 2.
- `message.properties` (`Properties | None`): метадані MQTT 5.0 (`ContentType`, `CorrelationData`, `ResponseTopic`, `UserProperty`, `MessageExpiryInterval`).

### Зворотний виклик `on_publish`

Викликається після завершення повного циклу підтвердження відправлення вихідного повідомлення:
- Для QoS 0: відразу після запису байтів пакета у вихідний мережевий буфер сокета.
- Для QoS 1: після отримання від брокера пакета підтвердження `PUBACK`.
- Для QoS 2: після завершення чотиристороннього рукостискання та отримання пакета `PUBCOMP`.

```python
def on_publish(
    client: Client,
    userdata: Any,
    mid: int,
    reason_code: ReasonCode,
    properties: Properties | None
) -> None
```

### Зворотні виклики `on_subscribe` та `on_unsubscribe`

Викликаються після отримання від брокера відповідей `SUBACK` та `UNSUBACK` відповідно.

```python
def on_subscribe(
    client: Client,
    userdata: Any,
    mid: int,
    reason_codes: list[ReasonCode],
    properties: Properties | None
) -> None

def on_unsubscribe(
    client: Client,
    userdata: Any,
    mid: int,
    reason_codes: list[ReasonCode],
    properties: Properties | None
) -> None
```

- `reason_codes` (`list[ReasonCode]`): список статусів підтвердження для кожного запитаного в підписці топіка. У MQTT 3.1.1 містить наданий брокером рівень QoS (`0`, `1`, `2`) або код `0x80` (`Failure`). У MQTT 5.0 містить деталізовані коди (наприклад, `GrantedQoS0`, `GrantedQoS1`, `GrantedQoS2`, `UnspecifiedError`, `NotAuthorized`, `TopicFilterInvalid`).

## 3. Методи керування з'єднанням, підписками та публікацією

### Методи `connect()` та `connect_async()`

```python
client.connect(
    host: str,
    port: int = 1883,
    keepalive: int = 60,
    bind_address: str = "",
    bind_port: int = 0,
    clean_start: bool = MQTT_CLEAN_START_FIRST_ONLY,
    properties: Properties | None = None
) -> ReasonCode

client.connect_async(
    host: str,
    port: int = 1883,
    keepalive: int = 60,
    bind_address: str = "",
    bind_port: int = 0,
    clean_start: bool = MQTT_CLEAN_START_FIRST_ONLY,
    properties: Properties | None = None
) -> None
```

- `connect()`: виконує синхронне блокувальне підключення сокета до сервера і повертає `ReasonCode`.
- `connect_async()`: не виконує миттєвого блокувального виклику `socket.connect()`; фактичне відкриття TCP-сокета делегується мережевому циклу `loop_start()` або `loop_forever()`.

### Методи `subscribe()` та `unsubscribe()`

```python
client.subscribe(
    topic: str | tuple[str, int | SubscribeOptions] | list[tuple[str, int | SubscribeOptions]],
    qos: int = 0,
    options: SubscribeOptions | None = None,
    properties: Properties | None = None
) -> tuple[ReasonCode, int]

client.unsubscribe(
    topic: str | list[str],
    properties: Properties | None = None
) -> tuple[ReasonCode, int]
```

Повертають кортеж `(result, mid)`. Якщо `result == ReasonCode.Success`, пакет `SUBSCRIBE` успішно поставлено у чергу відправлення, а ціле число `mid` можна використовувати для зіставлення відповіді у зворотному виклику `on_subscribe`.

Клас `SubscribeOptions` у MQTT 5.0 дозволяє налаштувати додаткові параметри підписки:
- `noLocal` (`bool`): якщо `True`, клієнт не отримуватиме повідомлення, які він сам опублікував у цей топік.
- `retainAsPublished` (`bool`): зберігати оригінальний прапорець Retain при доставці підписнику.
- `retainHandling` (`int`): `0` — надсилати збережені повідомлення під час кожної підписки; `1` — надсилати лише якщо такої підписки ще не існувало; `2` — взагалі не надсилати збережені повідомлення під час оформлення підписки.

### Метод `publish()`

```python
client.publish(
    topic: str,
    payload: bytes | str | int | float | None = None,
    qos: int = 0,
    retain: bool = False,
    properties: Properties | None = None
) -> MQTTMessageInfo
```

Метод повертає об'єкт `MQTTMessageInfo`, який надає інтерфейс контролю доставки:
- `info.rc` (`ReasonCode`): статус постановки повідомлення у вихідний буфер.
- `info.mid` (`int`): ідентифікатор повідомлення.
- `info.is_published()` (`bool`): повертає `True`, якщо повідомлення вже доставлене та підтверджене брокером.
- `info.wait_for_publish(timeout: float | None = None)`: блокує поточний потік до отримання підтвердження від брокера або до вичерпання таймауту.

## 4. Маршрутизація топіків через message_callback_add

Бібліотека дозволяє прив'язувати окремі спеціалізовані функції зворотного виклику до конкретних шаблонів топіків (включно з масками `+` та `#`), розвантажуючи головний метод `on_message`:

```python
client.message_callback_add(
    sub: str,
    callback: Callable[[Client, Any, MQTTMessage], None]
) -> None

client.message_callback_remove(sub: str) -> None
```

Якщо вхідне повідомлення відповідає зареєстрованому шаблону `sub`, клієнт викликає відповідну функцію. Якщо жоден шаблон не збігся, керування передається загальному обробнику `client.on_message`.

## 5. Безпека, буферизація та відмовостійкість

### Налаштування TLS/SSL

```python
client.tls_set(
    ca_certs: str | None = None,
    certfile: str | None = None,
    keyfile: str | None = None,
    cert_reqs: ssl.VerifyMode = ssl.CERT_REQUIRED,
    tls_version: int = ssl.PROTOCOL_TLS_CLIENT,
    ciphers: str | None = None,
    keyfile_password: str | None = None
) -> None

client.tls_set_context(context: ssl.SSLContext) -> None
client.tls_insecure_set(value: bool) -> None
```

Використання `tls_set_context()` є рекомендованим підходом у сучасних версіях Python: воно дозволяє повноцінно конфігурувати шифри, версії TLS 1.3, перевірку ланцюгів сертифікатів та завантажувати системні сховища ключів.

### Керування чергами та обмеження ресурсів

```python
client.reconnect_delay_set(min_delay: int = 1, max_delay: int = 120) -> None
client.max_queued_messages_set(queue_size: int) -> None
client.max_inflight_messages_set(inflight: int) -> None
```

- `reconnect_delay_set`: встановлює мінімальну та максимальну межу затримки експоненційного відступу (Exponential Backoff) при повторних спробах підключення.
- `max_queued_messages_set`: жорсткий ліміт кількості невідправлених повідомлень QoS 1/2 у внутрішній пам'яті під час відсутності мережевого з'єднання (запобігає вичерпанню пам'яті).
- `max_inflight_messages_set`: максимальна кількість одночасних транзакцій QoS 1/2, що перебувають у процесі підтвердження в мережі (за замовчуванням 20).
