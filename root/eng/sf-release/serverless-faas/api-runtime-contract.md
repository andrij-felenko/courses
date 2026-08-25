# 📋 Контракт середовища виконання: стандартизований Runtime API та життєвий цикл

Будь-яка платформа безсерверних обчислень потребує чіткої межі між внутрішньою інфраструктурою хоста (планувальником, чергами, моніторингом) та ізольованим кодом користувача. Замість того, щоб вбудовувати специфічні драйвери платформи всередину кожного мовного середовища, сучасні FaaS-системи використовують стандартизований протокол взаємодії через локальний HTTP-інтерфейс — **Runtime API** (англ. *Runtime Application Programming Interface*).

Цей контракт визначає, як користувацький процес ініціалізується, як отримує вхідні події, як повертає результати чи помилки, як передає потокові відповіді, як працює з шарами розширень і як система сигналізує про завершення життєвого циклу пісочниці.

## Життєвий цикл виконання (Execution Lifecycle)

Робота пісочниці FaaS поділяється на три чітко розмежовані фази: **Ініціалізація** (`Init`), **Виклик** (`Invoke`) та **Вимкнення** (`Shutdown`).

```
[Старт пісочниці / MicroVM]
       ↓
 ┌──────────────────────────────────────────────────────────┐
 │ Фаза Init (виконується один раз під час холодного старту)│
 │  1. Extension Init: запуск зовнішніх процесів моніторингу│
 │  2. Runtime Init: запуск мовного середовища (bootstrap)  │
 │  3. Function Init: виконання глобального коду та імпортів│
 └──────────────────────────────────────────────────────────┘
       ↓
 ┌──────────────────────────────────────────────────────────┐
 │ Фаза Invoke (повторюється для кожного запиту)            │
 │  1. GET /runtime/invocation/next  → отримання події      │
 │  2. Виконання функції: response = handler(event, context)│
 │  3. POST /runtime/invocation/{id}/response → відправка   │
 └──────────────────────────────────────────────────────────┘
       ↓ (період бездіяльності або оновлення конфігурації)
 ┌──────────────────────────────────────────────────────────┐
 │ Фаза Shutdown (виконується перед знищенням пісочниці)    │
 │  1. Сповіщення розширень про зупинку (SHUTDOWN event)    │
 │  2. Відправка сигналу SIGTERM процесу виконання          │
 │  3. Зупинка мікровіртуальної машини                      │
 └──────────────────────────────────────────────────────────┘
```

### 1. Фаза ініціалізації (`Init`)
Фаза `Init` виконується лише під час первинного холодного старту (англ. *cold start*) або створення додаткових паралельних пісочниць під час сплеску трафіку. Вона обмежена за часом (за замовчуванням до 10 секунд). Якщо процес ініціалізації не вкладається в ліміт або завершується аварійно, платформа надсилає помилку `Init Error` і знищує пісочницю.

Фаза складається з трьох послідовних кроків:
1. **Extension Init**: запуск додаткових агентів моніторингу та телеметрії (наприклад, OpenTelemetry чи Datadog агентів), якщо вони підключені у вигляді шарів (Layers);
2. **Runtime Init**: виконання стартового виконуваного файлу `bootstrap`, запуск інтерпретатора або віртуальної машини (V8, JVM, Python runtime);
3. **Function Init**: зчитування файлу функції, імпорт залежностей, створення екземплярів клієнтів баз даних, компіляція регулярних виразів та виконання будь-якого коду, розміщеного поза межами тіла функції-обробника (англ. *global scope*).

### 2. Фаза виклику (`Invoke`)
Після успішної ініціалізації процес входить у нескінченний цикл опитування. Процес надсилає блокуючий HTTP-запит до локального сервера Runtime API, очікуючи на прибуття нової події. Після надходження запиту викликається зареєстрований обробник (англ. *handler*). Після повернення результату платформа повертає відповідь клієнту, а пісочницю «заморожує» за допомогою контрольних груп cgroups або залишає очікувати наступного запиту.

### 3. Фаза вимкнення (`Shutdown`)
Якщо пісочниця не отримує нових запитів протягом визначеного часу (зазвичай 5–45 хвилин) або відбувається деплой нової версії коду, платформа ініціює вимкнення. Процесу середовища виконання надсилається системний сигнал `SIGTERM`, надаючи короткий часовий інтервал (від 300 до 2000 мілісекунд) для закриття відкритих файлів і завершення мережевих транзакцій, після чого надсилається `SIGKILL`.

---

## Синхронний проти асинхронного режиму виклику

Платформа FaaS підтримує два принципово різні режими виклику функцій з боку клієнтів, що визначає поведінку площини керування:

1. **Синхронний виклик (`RequestResponse`)**: клієнт (наприклад, веб-браузер через HTTP API Gateway) відкриває TCP-з'єднання і блокується в очікуванні відповіді. Площина керування FaaS негайно направляє подію у вільну пісочницю, очікує завершення виконання обробника і повертає згенероване тіло відповіді назад клієнту. Якщо всі пісочниці зайняті або сталася помилка, клієнт отримує код помилки безпосередньо.
2. **Асинхронний виклик (`Event`)**: джерело події (наприклад, сервіс Amazon S3 при завантаженні файлу або Amazon SNS) передає повідомлення у внутрішню чергу площини керування. Платформа миттєво повертає клієнту статус `202 Accepted` і бере на себе відповідальність за гарантовану доставку. 

Якщо під час асинхронного виклику функція зазнає аварії (повертає помилку через `POST /runtime/invocation/{id}/error` або аварійно завершується за тайм-аутом), FaaS-платформа автоматично виконує дві повторні спроби (англ. *retries*) з експоненційним відтермінуванням. Якщо всі спроби вичерпано без успіху, повідомлення не втрачається, а автоматично перенаправляється до черги мертвих листів (DLQ, англ. *Dead Letter Queue*) або відправляється у цільовий топік помилок EventBridge для ручного аналізу інженерами.

---

## Специфікація кінцевих точок Runtime API

Усередині пісочниці платформа підіймає локальний HTTP-сервер і передає його адресу через змінну оточення `AWS_LAMBDA_RUNTIME_API` (наприклад, `127.0.0.1:9001`). Спілкування відбувається за протоколом HTTP/1.1.

### 1. Отримання наступної події (Invocation Next)

Процес середовища виконання робить блокуючий запит `GET`, щоб отримати чергову подію для обробки. Якщо в черзі немає активних подій, HTTP-з'єднання утримується відкритим без повернення даних доти, доки зовнішня подія не надійде у площину керування.

```http
GET /2018-06-01/runtime/invocation/next HTTP/1.1
Host: 127.0.0.1:9001
User-Agent: custom-runtime/1.0
```

#### Заголовки відповіді сервера:

| Заголовок | Тип | Опис |
| :--- | :--- | :--- |
| `Lambda-Runtime-Aws-Request-Id` | `String (UUID)` | Унікальний ідентифікатор виклику. Обов'язковий для передачі у відповіді чи звіті про помилку. |
| `Lambda-Runtime-Deadline-Ms` | `Integer (Unix ms)` | Часова мітка епохи Unix у мілісекундах, коли виконання буде примусово перервано за тайм-аутом. |
| `Lambda-Runtime-Invoked-Function-Arn` | `String (ARN)` | Повний ARN (англ. *Amazon Resource Name*) викликаної функції або псевдоніма версії. |
| `Lambda-Runtime-Trace-Id` | `String` | Ідентифікатор розподіленого трейсингу (AWS X-Ray / W3C Trace Context). |
| `Lambda-Runtime-Client-Context` | `JSON string` | Контекст мобільного клієнта (за наявності, передається через AWS Mobile SDK). |
| `Lambda-Runtime-Cognito-Identity` | `JSON string` | Дані автентифікації користувача Amazon Cognito (за наявності). |

#### Приклад відповіді сервера:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Lambda-Runtime-Aws-Request-Id: 8456c325-ac52-4406-932b-31367098c408
Lambda-Runtime-Deadline-Ms: 1787184000100
Lambda-Runtime-Invoked-Function-Arn: arn:aws:lambda:eu-central-1:123456789012:function:process-payment:$LATEST
Lambda-Runtime-Trace-Id: Root=1-5e43ebd2-53ce0fd4205e4635832a8497;Parent=0ec9be1033280047;Sampled=1
Content-Length: 74

{"order_id": "ORD-94812", "amount": 149.50, "currency": "UAH", "user_id": 42}
```

---

### 2. Відправка успішної відповіді (Invocation Response)

Після успішного завершення роботи функції обробник передає згенероване тіло відповіді назад у платформу методом `POST`.

```http
POST /2018-06-01/runtime/invocation/8456c325-ac52-4406-932b-31367098c408/response HTTP/1.1
Host: 127.0.0.1:9001
Content-Type: application/json
Content-Length: 48

{"status": "success", "transaction_id": "TX-109"}
```

- `{AwsRequestId}` у шляху URI обов'язково має збігатися з ідентифікатором, отриманим у заголовку `Lambda-Runtime-Aws-Request-Id`;
- Тіло запиту містить результат роботи функції (серіалізований у JSON, HTML, текст або двійкові байти);
- Успішна відповідь сервера має код стану `202 Accepted`.

---

### 3. Потокова передача відповіді (Response Streaming)

Якщо функція генерує великий обсяг даних (наприклад, потокове відео, генерація файлів звітів чи відповіді генеративних нейромереж), середовище може використовувати механізм потокової передачі (англ. *Response Streaming*), який підтримує Chunked Transfer Encoding.

```http
POST /2018-06-01/runtime/invocation/8456c325-ac52-4406-932b-31367098c408/response HTTP/1.1
Host: 127.0.0.1:9001
Transfer-Encoding: chunked
Lambda-Runtime-Function-Response-Mode: streaming
Trailer: Lambda-Runtime-Function-Error-Type, Lambda-Runtime-Function-Error-Body

1a
{"chunk": 1, "data": "A"}
1a
{"chunk": 2, "data": "B"}
0
```

У разі виникнення помилки всередині генерації потоку, опис винятку передається у трейлер-заголовках `Lambda-Runtime-Function-Error-Type` та `Lambda-Runtime-Function-Error-Body` після фінального нульового чанка. Це дозволяє клієнту на іншому кінці з'єднання дізнатися про збій генерації, навіть якщо початкові HTTP-заголовки `200 OK` уже були відправлені у мережу.

---

### 4. Звіт про помилку виконання (Invocation Error)

Якщо під час роботи функції виник неперехоплений виняток або помилка бізнес-логіки, процес надсилає структурований звіт про аварію.

```http
POST /2018-06-01/runtime/invocation/8456c325-ac52-4406-932b-31367098c408/error HTTP/1.1
Host: 127.0.0.1:9001
Content-Type: application/json
Lambda-Runtime-Function-Error-Type: Unhandled

{
  "errorMessage": "Database connection timeout after 3000ms",
  "errorType": "ConnectionTimeoutException",
  "stackTrace": [
    "com.example.db.Pool.getConnection(Pool.java:42)",
    "com.example.Handler.handleRequest(Handler.java:18)"
  ]
}
```

Схема об'єкта помилки:

| Поле | Тип | Обов'язкове | Опис |
| :--- | :--- | :--- | :--- |
| `errorMessage` | `String` | Так | Текстове повідомлення про причину винятку. |
| `errorType` | `String` | Так | Назва класу помилки чи типу винятку. |
| `stackTrace` | `Array[String]` | Ні | Масив рядків трасування стека викликів. |

---

### 5. Фатальна помилка ініціалізації (Init Error)

Якщо аварія сталася на етапі `Init` (наприклад, файл модуля не знайдено, помилка синтаксису, збій завантаження динамічної бібліотеки), середовище надсилає звіт на спеціальний маршрут.

```http
POST /2018-06-01/runtime/init/error HTTP/1.1
Host: 127.0.0.1:9001
Content-Type: application/json
Lambda-Runtime-Function-Error-Type: Runtime.InitializationError

{
  "errorMessage": "Cannot find module './handler'",
  "errorType": "Runtime.ImportModuleError",
  "stackTrace": ["Module._resolveFilename (node:internal/modules/cjs/loader:1077:15)"]
}
```

Після надходження запиту `Init Error` платформа негайно фіксує аварійне завершення у системних логах і безповоротно знищує пісочницю.

---

## Стандартні контракти вхідних подій (Event Payload Schemas)

Залежно від тригера, корисне навантаження події має строго регламентовану структуру JSON.

### 1. HTTP API Gateway v2 Payload Format

Коли функція виступає бекендом для веб-запиту через API Gateway (формат корисного навантаження 2.0), вхідна подія має такий вигляд:

```json
{
  "version": "2.0",
  "routeKey": "POST /orders",
  "rawPath": "/orders",
  "rawQueryString": "source=web&ref=12",
  "headers": {
    "accept": "application/json",
    "content-type": "application/json",
    "host": "api.example.com",
    "user-agent": "Mozilla/5.0",
    "x-forwarded-for": "203.0.113.195"
  },
  "queryStringParameters": {
    "source": "web",
    "ref": "12"
  },
  "requestContext": {
    "accountId": "123456789012",
    "apiId": "r3pm45",
    "domainName": "api.example.com",
    "http": {
      "method": "POST",
      "path": "/orders",
      "protocol": "HTTP/1.1",
      "sourceIp": "203.0.113.195",
      "userAgent": "Mozilla/5.0"
    },
    "requestId": "JK482-94812",
    "routeKey": "POST /orders",
    "stage": "$default",
    "timeEpoch": 1787184000000
  },
  "body": "{\"item_id\": 99, \"quantity\": 2}",
  "isBase64Encoded": false
}
```

У відповідь функція зобов'язана повернути структуру з кодом стану HTTP:

```json
{
  "statusCode": 201,
  "headers": {
    "Content-Type": "application/json",
    "Cache-Control": "no-cache"
  },
  "body": "{\"order_id\": \"ORD-94812\", \"status\": \"created\"}",
  "isBase64Encoded": false
}
```

---

### 2. SQS Batch Event та часткова відмова пакету (Partial Batch Failure)

Коли FaaS-функція підписана на чергу повідомлень (Amazon SQS, RabbitMQ), платформа надсилає масив повідомлень у полі `Records`:

```json
{
  "Records": [
    {
      "messageId": "msg-001",
      "receiptHandle": "AQEBwJn...",
      "body": "{\"task\": \"send_email\", \"user\": \"alice@example.com\"}",
      "attributes": {
        "ApproximateReceiveCount": "1",
        "SentTimestamp": "1787184000000"
      },
      "messageAttributes": {},
      "md5OfBody": "faf8123...",
      "eventSource": "aws:sqs",
      "eventSourceARN": "arn:aws:sqs:eu-central-1:123456789012:task-queue",
      "awsRegion": "eu-central-1"
    },
    {
      "messageId": "msg-002",
      "receiptHandle": "AQEBxKp...",
      "body": "{\"task\": \"invalid_payload\"}",
      "attributes": {
        "ApproximateReceiveCount": "1",
        "SentTimestamp": "1787184000010"
      },
      "messageAttributes": {},
      "md5OfBody": "bbc9871...",
      "eventSource": "aws:sqs",
      "eventSourceARN": "arn:aws:sqs:eu-central-1:123456789012:task-queue",
      "awsRegion": "eu-central-1"
    }
  ]
}
```

Якщо друге повідомлення завершилося помилкою, але перше оброблено успішно, функція може повернути список лише тих ідентифікаторів, які зазнали збою:

```json
{
  "batchItemFailures": [
    {
      "itemIdentifier": "msg-002"
    }
  ]
}
```

Платформа видалить `msg-001` із черги як успішно виконане, а `msg-002` поверне в чергу для повторної спроби, уникнувши повторної обробки вже виконаних повідомлень.

---

### 3. S3 Object Notification Event

Подія про створення файлу в об'єктному сховищі:

```json
{
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "awsRegion": "eu-central-1",
      "eventTime": "2026-08-20T09:00:00.000Z",
      "eventName": "ObjectCreated:Put",
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "ImageResizeTrigger",
        "bucket": {
          "name": "user-uploads-bucket",
          "arn": "arn:aws:s3:::user-uploads-bucket"
        },
        "object": {
          "key": "photos/avatar_original.png",
          "size": 2048576,
          "eTag": "b10a8db164e0754105b7a99be72e3fe5",
          "sequencer": "0A1B2C3D4E5F678901"
        }
      }
    }
  ]
}
```

---

## Змінні оточення та системні ресурси всередині пісочниці

Платформа FaaS гарантовано передає у процес пісочниці набір стандартних змінних оточення:

| Змінна | Приклад значення | Призначення |
| :--- | :--- | :--- |
| `AWS_LAMBDA_RUNTIME_API` | `127.0.0.1:9001` | Хост і порт локального HTTP-сервера Runtime API. |
| `_HANDLER` | `index.handler` | Точка входу обробника, вказана в конфігурації. |
| `AWS_LAMBDA_FUNCTION_NAME` | `process-payment` | Назва функції. |
| `AWS_LAMBDA_FUNCTION_VERSION` | `$LATEST` | Версія функції або номер релізу. |
| `AWS_LAMBDA_FUNCTION_MEMORY_SIZE`| `512` | Виділений обсяг оперативної пам'яті в мегабайтах. |
| `AWS_LAMBDA_LOG_GROUP_NAME` | `/aws/lambda/process-payment` | Назва групи логів у системі моніторингу. |
| `AWS_LAMBDA_LOG_STREAM_NAME` | `2026/08/20/[$LATEST]abc123` | Назва потоку логів для поточного екземпляра пісочниці. |
| `LAMBDA_TASK_ROOT` | `/var/task` | Робочий каталог, куди розпаковано файли функції. |
| `LAMBDA_RUNTIME_DIR` | `/var/runtime` | Каталог системних бібліотек середовища. |
| `_X_AMZN_TRACE_ID` | `Root=1-5e...;Sampled=1` | Поточний контекст розподіленого трейсингу. |

Окрім змінних оточення, середовище виконання зчитує системні псевдофайли Linux для автоматичного налаштування пам'яті:
- У cgroups v1: ліміт пам'яті зчитується з файлу `/sys/fs/cgroup/memory/memory.limit_in_bytes`;
- У cgroups v2: ліміт пам'яті зчитується з файлу `/sys/fs/cgroup/memory.max`.

Віртуальні машини JVM та Node.js використовують ці файли для автоматичного визначення розміру купи (Heap size), запобігаючи несподіваному аварійному завершенню процесу через системний OOM Killer (англ. *Out-Of-Memory Killer*).

---

## Структура об'єкта контексту (Context Object)

У кожному мовному середовищі (Python, Node.js, Go, Java, C++) обробник приймає два аргументи: `event` (корисне навантаження події) та `context` (метадані поточного виклику). Об'єкт контексту синтезується середовищем виконання на основі заголовків, отриманих від Runtime API:

```
Context Object:
  ├── function_name: String          // Ім'я функції з $AWS_LAMBDA_FUNCTION_NAME
  ├── function_version: String       // Версія функції з $AWS_LAMBDA_FUNCTION_VERSION
  ├── invoked_function_arn: String   // ARN із заголовка Lambda-Runtime-Invoked-Function-Arn
  ├── memory_limit_in_mb: Integer    // Пам'ять із $AWS_LAMBDA_FUNCTION_MEMORY_SIZE
  ├── aws_request_id: String         // UUID із заголовка Lambda-Runtime-Aws-Request-Id
  ├── log_group_name: String         // Група логів
  ├── log_stream_name: String        // Потік логів
  └── get_remaining_time_in_millis() // Метод: (Deadline_Ms - Current_Unix_Time_Ms)
```

Метод `get_remaining_time_in_millis()` є критично важливим для забезпечення надійності: функція може періодично перевіряти залишок виділеного ліміту часу й коректно завершити транзакцію чи зберегти проміжний стан до того, як платформа примусово знищить процес за тайм-аутом.

---

## Модель безпеки, облікові дані та оновлення токенів (IAM & STS Contract)

Кожна FaaS-пісочниця виконується з прив'язкою до певної ролі безпеки (IAM Role). Платформа забезпечує автентифікацію через надання тимчасових криптографічних ключів, згенерованих сервісом маркерів безпеки (AWS STS, англ. *Security Token Service*).

Облікові дані передаються у пісочницю двома основними механізмами:
1. **Змінні оточення**: під час старту виставляються змінні `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` та `AWS_SESSION_TOKEN`. Вони мають обмежений термін дії (зазвичай від 1 до 6 годин);
2. **Локальний сервіс метаданих пісочниці** (англ. *Container Credentials Endpoint*): платформа надає локальний HTTP-інтерфейс за адресою `http://169.254.170.2$AWS_CONTAINER_CREDENTIALS_RELATIVE_URI`. 

Офіційні клієнтські бібліотеки (SDK) у фоновому режимі звертаються до цього маршруту для автоматичного оновлення тимчасових ключів до закінчення строку їхньої дії, що дозволяє тривалим пісочницям безперервно взаємодіяти з базами даних та чергами без ризику раптової втрати прав доступу.

---

## Структура артефактів та контракт підключення шарів (Layers)

Файлова система пісочниці організована за суворою схемою монтування:

```
Файлова система пісочниці:
  ├── /var/task              ← Код функції (розпакований zip-архів користувача)
  ├── /var/runtime           ← Системне середовище виконання (Node.js, Python, JVM)
  ├── /opt                   ← Змонтовані шари розширень (Layers)
  │     ├── /bin             ← Додається у системний шлях $PATH
  │     ├── /lib             ← Додається у системний шлях $LD_LIBRARY_PATH
  │     ├── /python          ← Додається у системний шлях $PYTHONPATH
  │     └── /nodejs          ← Додається у $NODE_PATH
  └── /tmp                   ← Єдиний доступний для запису диск (від 512 МБ до 10 ГБ)
```

Коли функція підключає кілька спільних шарів (наприклад, шар із попередньо скомпільованими динамічними бібліотеками `libvips` або `ffmpeg`), платформа накладає їх один на один у порядку зазначення конфігурації за допомогою файлової системи OverlayFS. Усі статичні файли в каталогах `/var/task` та `/opt` монтуються в режимі виключно для читання (`read-only`), а будь-які тимчасові файли або буфери повинні записуватися виключно у каталог `/tmp`.

---

## Контракт відновлення зі знімків пам'яті (Snapshot Restore Hooks)

Коли платформа використовує технологію швидкого відновлення зі знімків пам'яті (SnapStart / MicroVM Snapshotting), виникає проблема повторного використання стану:
1. Якщо генератор псевдовипадкових чисел (PRNG) був ініціалізований до створення знімка, усі відновлені екземпляри генеруватимуть однакові послідовності випадкових чисел (що руйнує безпеку криптографічних ключів, токенів та ідентифікаторів);
2. Відкриті мережеві TCP-з'єднання (до баз даних, кешів Redis) стають недійсними, оскільки віддалена сторона закриває їх за тайм-аутом під час простою знімка на диску.

Для вирішення цієї проблеми контракт середовища виконання надає спеціальні хуки життєвого циклу (англ. *Lifecycle Hooks*):
- `beforeCheckpoint()` — викликається перед збереженням стану пам'яті на диск. Тут функція зобов'язана закрити відкриті сокети, скинути буфери дисків і зупинити фонові таймери;
- `afterRestore()` — викликається негайно після відновлення пам'яті перед виконанням першого виклику `Invoke`. Тут середовище зобов'язане переініціалізувати ентропію генератора випадкових чисел через системний виклик `getrandom()` або `/dev/urandom` та заново підключитися до пулу баз даних.

---

## Обробка крайових випадків та системних сигналів ядра

Контракт виконання висуває суворі вимоги до обробки сигналів операційної системи Linux:

### 1. Тайм-аут виклику (Function Timeout)
Коли спливає час, виділений на виконання (наприклад, 15 секунд), платформа не чекає повернення HTTP-відповіді від функції. Планувальник хоста надсилає сигнал переривання процесу або негайно заморожує віртуальну машину, повертаючи клієнту код `504 Gateway Timeout`. Будь-які незавершені фонові запити процесу негайно обриваються.

### 2. Сигнал OOM Killer (Нестача пам'яті)
Якщо процес перевищує виділений ліміт пам'яті, підсистема ядра Linux cgroups надсилає процес-вбивцю `SIGKILL` (код завершення 137). Платформа перехоплює статус завершення дочірнього процесу й записує у логи помилку:
```
REPORT RequestId: 8456c325... Duration: 1240.12 ms Billed Duration: 1241 ms Memory Size: 512 MB Max Memory Used: 512 MB
Runtime.ExitError: Runtime exited with error: signal: killed
```

### 3. Очищення зомбі-процесів (Zombie Process Reaping)
Якщо функція запускає дочірні підпроцеси (наприклад, виклики утиліт через `exec()`), процес середовища виконання (який виступає `PID 1` усередині простору назв пісочниці) зобов'язаний коректно перехоплювати сигнал `SIGCHLD` та викликати системну функцію `waitpid()`. Без цього в системі накопичуються процеси-зомбі, що призводить до вичерпання таблиці дескрипторів ядра `/proc/sys/kernel/pid_max` і блокування подальших викликів.

---

## Інтерфейс розширень (Extensions API) та телеметрії (Telemetry API)

Сучасні безсерверні платформи дозволяють запускати допоміжні фонові процеси — **розширення** (англ. *Extensions*). Розширення виконуються паралельно з основним кодом для збору телеметрії, завантаження конфігурацій чи попереднього прогріву підключень.

### 1. Реєстрація розширення (`Register`)

```http
POST /2020-01-01/extension/register HTTP/1.1
Host: 127.0.0.1:9001
Lambda-Extension-Name: opentelemetry-collector
Content-Type: application/json

{
  "events": ["INVOKE", "SHUTDOWN"]
}
```

Сервер повертає унікальний ідентифікатор у заголовку `Lambda-Extension-Identifier`:

```http
HTTP/1.1 200 OK
Lambda-Extension-Identifier: ext-id-98124b8a-f721
Content-Type: application/json

{
  "functionName": "process-payment",
  "functionVersion": "$LATEST",
  "handler": "index.handler"
}
```

### 2. Синхронізація фаз життєвого циклу (`Next`)

Розширення надсилає блокуючий запит, очікуючи на чергову зміну стану пісочниці:

```http
GET /2020-01-01/extension/event/next HTTP/1.1
Host: 127.0.0.1:9001
Lambda-Extension-Identifier: ext-id-98124b8a-f721
```

Сервер повертає повідомлення про подію:
- При виклику функції: `{"eventType": "INVOKE", "deadlineMs": 1787184000100, "requestId": "..."}`
- При завершенні роботи пісочниці: `{"eventType": "SHUTDOWN", "shutdownReason": "spindown", "deadlineMs": 1787184002000}`

### 3. Telemetry API: підписка на системні логи та події

Замість перехоплення стандартного потоку `stdout/stderr` розширення може підписатися на структурований потік телеметрії (логи платформи, метрики пам'яті, часові мітки холодного старту):

```http
PUT /2022-07-01/telemetry HTTP/1.1
Host: 127.0.0.1:9001
Lambda-Extension-Identifier: ext-id-98124b8a-f721
Content-Type: application/json

{
  "schemaVersion": "2022-07-01",
  "types": ["platform", "function", "extension"],
  "buffering": {
    "maxItems": 1000,
    "maxBytes": 262144,
    "timeoutMs": 100
  },
  "destination": {
    "protocol": "HTTP",
    "URI": "http://sandbox.local:8080/telemetry"
  }
}
```

Платформа FaaS транслює логи безпосередньо за вказаною адресою локального сокета, усуваючи необхідність парсингу текстових логів.

---

## Еталонна реалізація Custom Runtime на C++

Завдяки простоті HTTP-інтерфейсу створення високопродуктивного середовища виконання на скомпільованій мові програмування не потребує важких фреймворків. Нижче наведено приклад ядра середовища виконання на C++20 з використанням RAII та HTTP-клієнта:

```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <cstdlib>
#include <format>
#include <chrono>
#include <curl/curl.h>

// Допоміжний клас RAII для керування дескриптором libcurl
class CurlHandle {
public:
    CurlHandle() : handle_(curl_easy_init()) {
        if (!handle_) throw std::runtime_error("Не вдалося ініціалізувати CURL");
    }
    ~CurlHandle() { if (handle_) curl_easy_cleanup(handle_); }
    CURL* get() const noexcept { return handle_; }

    CurlHandle(const CurlHandle&) = delete;
    CurlHandle& operator=(const CurlHandle&) = delete;
private:
    CURL* handle_;
};

// Зворотний виклик для запису тіла відповіді
static size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    auto* s = static_cast<std::string*>(userp);
    s->append(static_cast<char*>(contents), size * nmemb);
    return size * nmemb;
}

// Зворотний виклик для парсингу заголовків відповіді
static size_t HeaderCallback(char* buffer, size_t size, size_t nitems, void* userp) {
    size_t total = size * nitems;
    std::string_view header(buffer, total);
    auto* req_id = static_cast<std::string*>(userp);
    
    constexpr std::string_view target = "lambda-runtime-aws-request-id:";
    if (header.size() >= target.size()) {
        // Порівняння без урахування регістру перших байтів
        bool match = true;
        for (size_t i = 0; i < target.size(); ++i) {
            if (std::tolower(header[i]) != target[i]) { match = false; break; }
        }
        if (match) {
            auto val = header.substr(target.size());
            // Видалення пробілів та символів переносу рядка
            while (!val.empty() && (val.front() == ' ' || val.front() == '\t')) val.remove_prefix(1);
            while (!val.empty() && (val.back() == '\r' || val.back() == '\n' || val.back() == ' ')) val.remove_suffix(1);
            *req_id = std::string(val);
        }
    }
    return total;
}

// Бізнес-логіка обробника події
std::string HandleEvent(std::string_view payload, std::string_view request_id) {
    // Демонстраційна обробка: генерація відповіді JSON
    return std::format(R"({{"status":"success","request_id":"{}","processed_bytes":{}}})", 
                       request_id, payload.size());
}

int main() {
    // 1. Фаза Init: зчитування адреси Runtime API
    const char* api_env = std::getenv("AWS_LAMBDA_RUNTIME_API");
    if (!api_env) {
        std::cerr << "Помилка: AWS_LAMBDA_RUNTIME_API не встановлено\n";
        return 1;
    }
    const std::string runtime_api = api_env;
    const std::string next_url = std::format("http://{}/2018-06-01/runtime/invocation/next", runtime_api);

    curl_global_init(CURL_GLOBAL_ALL);

    // 2. Нескінченний цикл фази Invoke
    while (true) {
        CurlHandle curl;
        std::string response_body;
        std::string request_id;

        curl_easy_setopt(curl.get(), CURLOPT_URL, next_url.c_str());
        curl_easy_setopt(curl.get(), CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl.get(), CURLOPT_WRITEDATA, &response_body);
        curl_easy_setopt(curl.get(), CURLOPT_HEADERFUNCTION, HeaderCallback);
        curl_easy_setopt(curl.get(), CURLOPT_HEADERDATA, &request_id);

        CURLcode res = curl_easy_perform(curl.get());
        if (res != CURLE_OK || request_id.empty()) {
            std::cerr << "Помилка отримання події: " << curl_easy_strerror(res) << "\n";
            continue;
        }

        // Виклик користувацького обробника
        std::string result = HandleEvent(response_body, request_id);

        // 3. Відправка результату назад у Runtime API
        std::string post_url = std::format("http://{}/2018-06-01/runtime/invocation/{}/response", 
                                           runtime_api, request_id);
        
        CurlHandle post_curl;
        curl_easy_setopt(post_curl.get(), CURLOPT_URL, post_url.c_str());
        curl_easy_setopt(post_curl.get(), CURLOPT_POSTFIELDS, result.c_str());
        curl_easy_setopt(post_curl.get(), CURLOPT_POSTFIELDSIZE, result.size());

        struct curl_slist* headers = nullptr;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(post_curl.get(), CURLOPT_HTTPHEADER, headers);

        curl_easy_perform(post_curl.get());
        curl_slist_free_all(headers);
    }

    curl_global_cleanup();
    return 0;
}
```

Така стандартизована модель взаємодії повністю ізолює інфраструктуру платформи від мовних середовищ, забезпечуючи високу швидкість обробки подій та стабільність FaaS-інфраструктури.
