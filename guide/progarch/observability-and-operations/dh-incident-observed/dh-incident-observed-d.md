# Інцидент очима телеметрії DH

<preknowlist>
- [Структуровані логи](book:programming/operations/structured-logging) — подія як JSON з контекстом замість сліпого текстового рядка.
- [Метрики](book:programming/operations/metrics-monitoring) — часові ряди, гістограми та перцентилі p95/p99 для виявлення деградації системи.
- [Розподілений трейсинг](book:programming/operations/distributed-tracing) — пересилання `traceparent` крізь сервіси для побудови спанів і зв'язування викликів.
- [Реляційне сховище як рішення](guide:progarch/storage-as-decision) — планувальник запитів, індексація та блокування рядків у реляційних базах даних.
</preknowlist>

О 14:15 у житлових комплексах Digital Homes мешканці перестають відчиняти вхідні двері під'їздів і паркінгів із мобільного застосунку. Натискання кнопки в інтерфейсі висне на десятки секунд і завершується помилкою таймауту, а розумні настінні панелі в квартирах втрачають зв'язок із центральним шлюзом поверху. Крайовий маршрутизатор Envoy фіксує сплеск деградації: дев'яносто дев'ятий перцентиль часу відповіді (p99 latency) для API відчинення дверей та отримання стану пристроїв злітає з нормальних `45 ms` до `14 200 ms`, а частість помилок родини 5xx перетинає поріг спрацьовування тривоги й досягає `4.8%` усіх вхідних запитів.

![Воронка розслідування інциденту: Prometheus виявляє p99 latency -> Exemplar TraceID переводить до OpenTelemetry span waterfall -> Loki знаходить термінальну помилку та лок у PostgreSQL](/guide/progarch/observability-and-operations/dh-incident-observed/img/telemetry-triage-funnel.svg)
*Триланковий маршрут локалізації збою. Метрики фіксують відхилення перцентиля й дають місток-Exemplar; трейси вказують на конкретний повільний спан бази даних; структурований лог викриває фізичну причину — неіндексований JSONB-запит і каскадне блокування рядків.*

Телеметрія (від грец. *tele* — далеко і *metron* — вимірювання) розподіленої системи — це не три окремі інструменти, куплені в різних вендорів, а єдина фізична картина виконання коду, представлена в трьох проекціях: метриках, трейсах і логах. Спроба розслідувати подібний збій «наосліп» — шляхом почергового перезапуску мікросервісів або випадкового читання терабайтної стрічки текстових логів — перетворює усунення аварії на багатогодинне вгадування. Нижче розібрано, як повна кореляція (від лат. *correlatio* — співвідношення) трьох стовпів телеметрії дозволяє за три хвилини пройти шлях від загального сигналу тривоги в Prometheus до конкретного неіндексованого SQL-запиту в PostgreSQL, що заблокував транзакційну базу.

---

## 1. Архітектурний контекст та топологія системи Digital Homes

Для розуміння масштабу інциденту розглянемо топологію бекенду Digital Homes під час пікового вечірнього навантаження. Система обслуговує 180 000 розумних квартир у 40 житлових комплексах. У момент інциденту о 14:15 мережевий трафік розподілявся наступним чином:

```
[Мобільні застосунки / Панелі] 
              │
              ▼ (12 000 req/min)
    [Envoy Edge Gateway Cluster]
              │
              ├──────► [Automation API Gateway] (Node.js / C++)
              │              │
              │              ▼
              └──────► [Device Telemetry Service] (C++ / Go)
                             │
                             ├──────► [Redis Primary Cache Cluster]
                             │
                             └──────► [PostgreSQL Primary DB Cluster]
                                      (45 000 000 рядків телеметрії)
```

Запити від мобільних застосунків мешканців надходять на кластер Envoy Edge Gateway, який здійснює аутентифікацію, перевірку токенів доступу та маршрутизацію до внутрішніх мікросервісів `automation-gateway` та `device-telemetry-service`. Сервіс телеметрії зберігає поточний стан пристроїв у Redis-кеші, а всю історію подій та оновлення статусу давачів записує у кластер PostgreSQL.

---

## 2. Перша ланка: Метрики підказують «що сталося», але мовчать про «чому»

Аварія починається із системи спостереження за метриками. Prometheus кожні 15 секунд опитує ендпоінтри `/metrics` усіх екземплярів Envoy, API-шлюзів та мікросервісів Digital Homes. Метрики — це агреговані числові часові ряди (time series), позбавлені індивідуального контексту окремих користувачів чи пристроїв.

### 2.1. Агрегація перцентилів та пастка середнього значення

Перша помилка чергового інженера — дивитися на середній час відповіді (p50 або arithmetic mean). Під час інциденту о 14:15 медіана p50 для `POST /api/v2/devices/unlock` залишалася на рівні `18 ms`. Чому? У цей момент 95% запитів відкриття дверей проходили через оперативний кеш Redis й виконувалися миттєво. Проблема зачіпала лише 5% запитів, для яких виклики збігалися з фоновим вичитанням історії телеметрії давачів.

Але для системи smart home збій 5% запитів — це тисячі людей перед зачиненими дверми. Для виявлення хвостів розподілу використовується 99-й перцентиль, обчислений за гістограмами Prometheus:

```
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{app="dh-gateway"}[2m])) by (le))
```

Обчислення виконується за бакетами гістограми. Бакет `http_request_duration_seconds_bucket{le="0.5"}` підраховує кількість запитів, швидших за 500 мілісекунд, а бакет `{le="+Inf"}` — усі запити. Коли лічильник бакета `le="10.0"` зупиняється, а `le="+Inf"` стрімко зростає, формула quantile підтверджує: p99 сягнув `14.2 s`.

```
Рівень затримки (Latency):
----------------------------------------------------------------------
p50 (медіана) :  18 ms  [====================] (норма)
p90           :  45 ms  [========================================]
p99 (хвіст)   : 14200 ms [===================================================>] (АВАРІЯ!)
```

Такий розподіл показує класичний «важкий хвіст» (heavy tail). Високі перцентилі сигналізують про наявність ресурсної контенції (resource contention) або блокувань, де більшість запитів чекають на звільнення спільного ресурсу.

#### Математичний механізм лінійної інтерполяції гістограм Prometheus

Prometheus обчислює quantile за допомогою лінійної інтерполяції між межами бакетів гістограми. Якщо загальна кількість вимірювань за 2 хвилини становить `N`, а розрахункова позиція 99-го перцентиля `rank = 0.99 × N` потрапляє в бакет між нижньою межею `q_{k-1}` та верхньою межею `q_k` із лічильниками `count_{k-1}` та `count_k`, обчислений перцентиль становить:

```
p99 = q_{k-1} + (q_k - q_{k-1}) × (rank - count_{k-1}) ÷ (count_k - count_{k-1})
```

Якщо бакети налаштовані недостатньо гранулярно (наприклад, між `1.0s` та `10.0s`), інтерполяція може показувати усереднене значення, хоча реальні запити падали за таймаутом на межі `14.0s`. Тому точні межі гістограм мають вирішальне значення для спостережуваності.

---

### 2.2. Обмеження високої кардинальності (High Cardinality Trap)

Чому ми не можемо додати `device_id`, `user_id` або `home_id` безпосередньо в мітки (labels) Prometheus-метрики `http_request_duration_seconds`? 

Якби ми додали мітку `device_id`, кількість часових рядків дорівнювала б:

```
N_series = N_services × N_endpoints × N_buckets × N_devices
         = 20 × 50 × 12 × 500 000 = 600 000 000 часових рядків
```

Спроба зберегти 600 мільйонів часових рядків у Prometheus призводить до миттєвого вичерпання оперативної пам'яті (OOM-Killed) та краху бази даних метрик. Метрики свідомо роблять німими до конкретних ідентифікаторів. Вони кажуть: *«Сервіс dh-gateway має сплеск p99 на ендпоінті /unlock»*, але вони неспроможні відповісти, яка саме транзакція чи який пристрій викликає деградацію.

---

### 2.3. Зв'язуючий місток: Prometheus Exemplars

Щоб поєднати абсолютну агрегацію метрик із деталізацією трейсів, специфікація OpenMetrics вводить **Exemplars** (екземпляри). Коли Prometheus опитує сервіс, разом із числом бакета гістограми сервіс додає один конкретний ідентифікатор трейсу (`trace_id`), який потрапив у цей часовий інтервал:

```http
http_request_duration_seconds_bucket{le="+Inf",path="/api/v2/devices/unlock"} 149200 # {trace_id="4bf92f3577b34da6a3ce929d0e0e4736"} 14.21 1771402514.280
```

Клацаючи на точку графіку p99 у Grafana, інженер не шукає наосліп у базі: графік за допомогою Exemplar містить пряме посилання на унікальний ідентифікатор трасування `4bf92f3577b34da6a3ce929d0e0e4736`.

> 🔧 **Навіщо це.** Без Exemplars перехід від алерта Prometheus до системи трейсингу (Jaeger або Tempo) вимагав ручного копіювання часових міток і здогадок. Exemplar перетворює метрику на покажчик: точка на графіку деградації прямо посилається на унікальний ідентифікатор потоку виконання.

---

## 3. Друга ланка: Розподілений трейсинг локалізує затримку у водоспаді спанів

Отримавши `trace_id = 4bf92f3577b34da6a3ce929d0e0e4736`, оператор відкриває інтерфейс розподіленого трейсингу. Контекст (від лат. *contextus* — з'єднання) трасування дозволяє відтворити повне дерево викликів крізь межі процесів і мережі.

![Шлях поширення W3C traceparent заголовка від Envoy Edge Proxy крізь сервіси до PostgreSQL з експортом у три стовпи телеметрії](/guide/progarch/observability-and-operations/dh-incident-observed/img/w3c-traceparent-propagation.svg)
*Наскрізне прокидання контексту. Envoy генерує traceparent, microservice-gateway витягає його й передає у gRPC метаданих до device-telemetry-service. Кожен сервіс прокидає trace_id у структуровані JSON-логи, додає Exemplars у Prometheus та експортує спани в OpenTelemetry Collector.*

### 3.1. Анатомія W3C Trace Context

Шлюз Envoy на вході в контур Digital Homes створив W3C-заголовок `traceparent` і прокинув його в HTTP/2 запиті до внутрішніх сервісів. Заголовок має строго визначену специфікацію:

```
00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
│  │                               │                └─ TraceFlags (01 = Sampled)
│  │                               └─ ParentSpanID (64 біти hex)
│  └─ TraceID (128 бітів hex)
└─ Version (00)
```

1. **TraceID** (`4bf92f35...`): залишається незмінним уздовж усього ланцюга. За ним шукають усі події в усіх сервісах.
2. **SpanID** (`00f067aa...`): ідентифікує конкретний відрізок роботи всередині одного сервісу.
3. **TraceFlags** (`01`): прапорець вибірки (sampling). `01` вказує всім наступним вузлам обов'язково зберегти деталі цього спану.

Детальний технічний розбір структури бітів та пар `tracestate` винесено в [специфікацію W3C Trace Context та схему атрибутів OpenTelemetry](guide:progarch/observability-and-operations/dh-incident-observed/api-otel-tracecontext.md).

---

### 3.2. Аналіз водоспаду спанів (Trace Waterfall)

У дашборді трасування інженер бачить наступне графічне дерево тривалості операцій:

```
[Service & Span Name]                    [Duration]  [Timeline Chart: 0s ......... 14.25s]
-----------------------------------------------------------------------------------------
1. envoy-edge : POST /unlock             14.25 s     [===================================]
  2. automation-gateway : ProcessCmd     14.23 s      [==================================]
    3. device-telemetry-svc : ExecSync   14.21 s       [=================================]
      4. db:pg_exec : SELECT telemetry   14.18 s        [================================] (SLOW!)
```

Аналіз водоспаду миттєво відсікає підозри від 19 мікросервісів:
* Envoy Edge Proxy витратив на власну обробку лише `0.02 s` (`14.25 - 14.23`).
* `automation-gateway` чекав на відповідь нижче за течією `0.02 s`.
* `device-telemetry-svc` застряг на `14.21 s`.
* **Вузьке місце (Bottleneck)**: дочірній спан `db:pg_exec`, виклик до бази даних PostgreSQL, тривав `14.18 s` із загальних `14.25 s`.

Трейс довів, що мережевий шар, TLS-хендшейки та gRPC-серіалізація не винні. Винуватець — конкретний виклик до бази даних у сервісі телеметрії. Проте сам спан OpenTelemetry містить лише атрибути `db.statement` та `db.system = postgresql`. Всі деталі стану транзакцій, контеншну блокувань (lock contention) та вмісту пам'яті опиняються в третій ланці — логах.

---

## 4. Третя ланка: Структурований лог розкриває фізичну причину

Для остаточного встановлення причини інженер бере з трейсу два ідентифікатори: `trace_id = 4bf92f3577b34da6a3ce929d0e0e4736` та `span_id = 5c067aa0ba902b71`.

У панелі пошуку логів Loki виконується запит за індексованим полем:

```logql
{app="device-telemetry-service"} |= "4bf92f3577b34da6a3ce929d0e0e4736"
```

### 4.1. Знайдений структурований JSON-лог

Система агрегації повертає точний JSON-запис, згенерований логером сервісу при виникненні таймауту:

```json
{
  "timestamp": "2026-08-18T14:15:14.280Z",
  "level": "ERROR",
  "service": "device-telemetry-service",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "5c067aa0ba902b71",
  "home_id": "dh-kyiv-0841",
  "device_id": "lock-front-door-991",
  "message": "Database query failed due to statement timeout",
  "db": {
    "query_duration_ms": 14180,
    "lock_wait_ms": 14100,
    "statement": "SELECT * FROM device_telemetry_events WHERE payload->>'status' = 'offline' AND created_at > NOW() - INTERVAL '1 hour'"
  },
  "error": {
    "type": "QueryFailedError",
    "code": "55P03",
    "message": "canceling statement due to statement timeout"
  }
}
```

Одночасно в журналах бази даних PostgreSQL (системний модуль `auto_explain` та `log_lock_waits`) з'являється запис із відповідним `trace_id`, прокинутим через коментар SQL-запиту (`/* traceparent='00-4bf92f...' */`):

```text
2026-08-18 14:15:14.250 EEST [48210] LOG: process 48210 acquired ExclusiveLock on tuple (4851, 12) of relation "device_telemetry_events" after 14100.412 ms
2026-08-18 14:15:14.250 EEST [48210] STATEMENT: SELECT * FROM device_telemetry_events WHERE payload->>'status' = 'offline'...
```

---

### 4.2. Місток до Модуля 12: Чому бази даних вибухають під навантаженням

Тут розслідування телеметрії перетинається з архітектурою зберігання даних. Запит вичитує події з таблиці `device_telemetry_events` обсягом 45 мільйонів рядків за виразом `payload->>'status'`.

1. **Відсутність виразного індексу**: У ранковому релізі розробники додали фільтрацію JSONB-поля `payload->>'status'`, але забули створити індекс `CREATE INDEX ON device_telemetry_events ((payload->>'status'))`.
2. **Sequential Scan**: Планувальник запитів PostgreSQL змушений сканувати всі 45 мільйонів рядків з диска (Sequential Scan).
3. **Ескалація блокувань (Lock Escalation)**: Фоновий процес оновлення статусу давачів виконував `UPDATE device_telemetry_events SET payload = ...` всередині довгої транзакції. Повільний `SELECT` без індексу натрапив на рядочне блокування (Row Lock) й заблокував вичитування транзакції.
4. **Каскадна відмова**: Оскільки басейн з'єднань (connection pool) сервісу `device-telemetry-service` заповнився 100 повільними запитами, всі наступні запити на відчинення дверей (`POST /unlock`) вишикувалися в чергу чекання вільного сокета бази й впали за таймаутом `14 s`.

---

## 5. Кордон між трьома стовпами: Порівняльна матриця телеметрії

Кожен із трьох стовпів має власну цінову та функціональну оптимізацію. Спроба замінити один стовп іншим призводить або до втрати видимості, або до фінансового збанкрутування через рахунки за інфраструктуру телеметрії.

| Параметр | Метрики (Metrics) | Трейси (Traces) | Логи (Logs) |
| :--- | :--- | :--- | :--- |
| **Основне питання** | *«Що й коли зламалося?»* (Сигнал) | *«Де саме проблема?»* (Локалізація) | *«Чому це сталося?»* (Фізична причина) |
| **Формат даних** | Агреговані часові ряди, float64 counters/gauges. | Дерево спанів (DAG) з часовими інтервалами. | Неструктурований текст або структуровані JSON-об'єкти. |
| **Кардинальність** | Низька (обмежена набором фіксованих міток). | Висока (містить унікальні `TraceID`, `SpanID`). | Максимальна (будь-які атрибути, дампами помилок і стеками). |
| **Ціна збереження** | Дуже низька (байти на метрику). | Середня (потребує семплінгу/вибірки). | Висока (індексація й обсяг текстових файлів). |
| **Швидкість пошуку** | Субсекундна (за розрахованими бакетами). | Секундна (за ідентифікатором `trace_id`). | Від секунд до хвилин (за залежністю від індексів). |
| **Приклад технології** | Prometheus, VictoriaMetrics, Datadog metrics. | OpenTelemetry, Jaeger, Tempo, Zipkin. | Grafana Loki, Elasticsearch, OpenSearch, ClickHouse. |

---

### 5.1. Архітектурні пастки розриву телеметрії

Під час побудови спостережуваності Digital Homes інженери натрапляють на три типові пастки, коли три стовпи втрачають зв'язок між собою:

#### Пастка 1: Розрив контексту на асинхронних межах (Async Context Loss)
Якщо код передає задачу у фоновий пучок потоків (thread pool) або в асинхронний циклічний обробник (Event Loop `setImmediate`) без копіювання `traceparent`, новий потік генерує порожній контекст. У результаті лог помилки пишеться з `trace_id = "none"`, і знайти його за трейсом користувача стає неможливо.

#### Пастка 2: Рассинхронізація вибірки (Sampling Mismatch)
Метрики рахуються для **100%** вхідних запитів. Проте розподілений трейсинг через великий обсяг часто використовує вибірку на вході (Head-based sampling = 1%). Якщо повільний запит p99 потрапив у 99% відкинутих трейсів, Exemplar не зможе відкрити спан, бо його не було збережено. Для критичних помилок слід застосовувати вибірку на виході (Tail-based sampling), яка зберігає 100% трейсів із кодами відповіді `5xx` або latency `> 2s`.

#### Пастка 3: Зрізання заголовків на проксі (Proxy Header Stripping)
Якщо зовнішній мережевий екран (WAF) або чужий корпоративний проксі видаляє неприпустимий заголовок `traceparent` з HTTP-запиту, шлюз на вході сприймає запит як новий і ґенерує новий `TraceID`. Для запобігання підробці `TraceID` ззовні Edge Proxy повинен перезаписувати `traceparent` для зовнішніх клієнтів, але надійно зберігати його між внутрішніми мікросервісами.

---

## 6. Прокидання контексту телеметрії Digital Homes у коді

Для забезпечення цілісності телеметрії розробники Digital Homes використовують єдині обгортки логування та прокидання контексту на C++ та TypeScript/Go.

Повну виробничу реалізацію мікросервісного middleware із підтримкою W3C `traceparent` та ін'єкцією в логери наведено в [практичній реалізації прокидання телеметрії в бекенді Digital Homes](guide:progarch/observability-and-operations/dh-incident-observed/proj-dh-telemetry-correlation.md).

Нижче показано фрагмент, де сервіс прийому телеметрії автоматично збагачує структурований JSON-лог та створює спан OpenTelemetry під час обробки виклику:

:::tabs
```cpp
// C++20 / OpenTelemetry C++ SDK / Scoped Trace Context
#include <iostream>
#include <string>
#include <memory>
#include <chrono>

// Обгортка для автоматичного додавання trace_id до кожного запису логу
class TelemetryScopedLogger {
public:
    static void log_db_error(const std::string& trace_id, 
                             const std::string& span_id, 
                             const std::string& query, 
                             double duration_ms, 
                             const std::string& error_msg) {
        auto now = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();

        std::cout << "{"
                  << "\"timestamp\":" << now << ","
                  << "\"level\":\"ERROR\","
                  << "\"service\":\"device-telemetry-service\","
                  << "\"trace_id\":\"" << trace_id << "\","
                  << "\"span_id\":\"" << span_id << "\","
                  << "\"db\":{"
                  << "\"statement\":\"" << query << "\","
                  << "\"duration_ms\":" << duration_ms
                  << "},"
                  << "\"error\":\"" << error_msg << "\""
                  << "}\n";
    }
};
```
```ts
// TypeScript / Node.js / OpenTelemetry Tracer & Pino Logger Integration
import { trace, context, SpanStatusCode } from '@opentelemetry/api';
import pino from 'pino';

const tracer = trace.getTracer('device-telemetry-service', '2.1.0');
const logger = pino({ name: 'device-telemetry-service' });

export async function executeCorrelatedQuery(sqlQuery: string, params: any[]) {
  // Отримуємо поточний активний спан з контексту OpenTelemetry
  const currentSpan = trace.getSpan(context.active());
  const traceId = currentSpan?.spanContext().traceId ?? 'unknown-trace-id';
  const spanId = currentSpan?.spanContext().spanId ?? 'unknown-span-id';

  const startTime = Date.now();

  // Створюємо дочірній спан клієнта бази даних
  return tracer.startActiveSpan('db:pg_exec', async (dbSpan) => {
    dbSpan.setAttribute('db.system', 'postgresql');
    dbSpan.setAttribute('db.statement', sqlQuery);

    try {
      // Симуляція запиту до бази
      const result = await dbClientQuery(sqlQuery, params);
      dbSpan.setStatus({ code: SpanStatusCode.OK });
      return result;
    } catch (err: any) {
      const durationMs = Date.now() - startTime;

      // Фіксуємо помилку у спані
      dbSpan.setStatus({ code: SpanStatusCode.ERROR, message: err.message });
      dbSpan.recordException(err);

      // Логуємо структурований JSON з обов'язковими полями trace_id та span_id
      logger.error({
        trace_id: traceId,
        span_id: spanId,
        db: { statement: sqlQuery, duration_ms: durationMs },
        err: { message: err.message, code: err.code }
      }, 'Помилка виконання SQL запиту в базі даних');

      throw err;
    } finally {
      dbSpan.end();
    }
  });
}

async function dbClientQuery(query: string, params: any[]) {
  // Імітація роботи БД
  return [];
}
```
```go
// Go 1.22 / OpenTelemetry Go / Structured JSON Logging
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/trace"
)

type StructuredLog struct {
	Timestamp string `json:"timestamp"`
	Level     string `json:"level"`
	Service   string `json:"service"`
	TraceID   string `json:"trace_id"`
	SpanID    string `json:"span_id"`
	Message   string `json:"message"`
	Duration  int64  `json:"duration_ms"`
}

func ExecuteDatabaseQuery(ctx context.Context, tracer trace.Tracer, query string) error {
	// Створюємо новий спан у контексті Go
	ctx, span := tracer.Start(ctx, "db:pg_exec",
		trace.WithSpanKind(trace.SpanKindClient),
		trace.WithAttributes(attribute.String("db.system", "postgresql")),
	)
	defer span.End()

	sc := span.SpanContext()
	traceID := sc.TraceID().String()
	spanID := sc.SpanID().String()

	start := time.Now()
	// Симуляція повільного запиту
	err := simulateQueryExecution()
	duration := time.Since(start).Milliseconds()

	if err != nil {
		span.RecordError(err)

		// Формуємо лог із чітко прив'язаним TraceID та SpanID
		logEntry := StructuredLog{
			Timestamp: time.Now().UTC().Format(time.RFC3339),
			Level:     "ERROR",
			Service:   "device-telemetry-service",
			TraceID:   traceID,
			SpanID:    spanID,
			Message:   fmt.Sprintf("DB query failed: %v", err),
			Duration:  duration,
		}
		bytes, _ := json.Marshal(logEntry)
		fmt.Println(string(bytes))
		return err
	}

	return nil
}

func simulateQueryExecution() error {
	return fmt.Errorf("canceling statement due to statement timeout")
}
```
:::

---

## 7. Усунення наслідків та запобігання інцидентам

Після того, як корельована телеметрія показала точне місце й фізичну причину аварії, чергова команда за 10 хвилин реалізує три рівні захисту:

1. **Технічне усунення (Quick Fix)**: Додавання виразного індексу в PostgreSQL для гарячого JSONB-поля:
   ```sql
   CREATE INDEX CONCURRENTLY idx_device_telemetry_status 
   ON device_telemetry_events ((payload->>'status')) 
   WHERE payload->>'status' IS NOT NULL;
   ```
   Після побудови індексу час виконання запиту знижується з `14 180 ms` до `1.2 ms`, а p99 latency Envoy повертається до норми `42 ms`.

2. **Захисне обмеження (Defensive Guardrails)**: Встановлення жорсткого таймауту сесії на рівні бази даних (`SET statement_timeout = '2000ms'`), щоб один неоптимальний запит не міг тримати блокування транзакцій понад 2 секунди й викликати каскадний вал аварій.

3. **Архітектурні ворота якості (CI Telemetry Linting)**: Впровадження автоматичного тесту в конвеєр CI/CD, який перевіряє всі нові SQL-запити через `EXPLAIN (FORMAT JSON)` і блокує деплой коду, якщо планувальник обирає `Sequential Scan` на таблицях обсягом понад 100 000 рядків.

Завдяки зв'язці трибічної телеметрії інцидент пройшов повний цикл — від спрацювання перцентильного алерта в Prometheus до виправлення виразного індексу в базі даних — без виснажливого «гадання на логах» та без ризикованих перезапусків сервісів наосліп.
