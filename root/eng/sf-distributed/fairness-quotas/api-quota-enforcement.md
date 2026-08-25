# 📋 Інтерфейс та протокол розподіленого квотування

У розподілених системах виконання квот та забезпечення справедливості реалізується на межі мережі (API Gateway, Ingress Controller) через стандартизовані сервісні контракти. 

Коли система складається з десятків географічно розподілених вузлів шлюзів і обслуговує мільйони запитів на секунду, неможливо виконувати синхронний виклик до центральної бази даних на кожен HTTP-запит. Затримка мережевого перельоту (Round-Trip Time) у 5 мілісекунд збільшила б затримку API в десятки разів, а саме сховище квот стало б єдиною точкою відмови та головним вузьким місцем усієї платформи.

Для вирішення цієї проблеми застосовують дворівневу архітектуру: на першому рівні (L1) вхідні проксі здійснюють миттєву перевірку в пам'яті через локальні алгоритми Token Bucket, а на другому рівні (L2) фонові процеси виконують періодичний лізинг пакетів квот у центрального координатора (Redis або Raft-кластера).

Нижче наведено повну специфікацію інтерфейсів системи розподіленого квотування: gRPC-протокол лізингу квот, структуру HTTP-заголовків стандарту IETF, атомарний Lua-скрипт для Redis, конфігурацію фільтра Envoy Proxy та інженерні гарантії відмовостійкості.

## 1. gRPC-контракт сервісу квот (Quota Lease Service)

Для мінімізації накладних витрат шлюзи використовують пакетний асинхронний лізинг токенів через високопродуктивний протокол gRPC. Замість того, щоб списувати 1 токен на кожен виклик, шлюз запитує пачку токенів на фіксований часовий інтервал (наприклад, 200 токенів на 500 мілісекунд).

Локальний бакет шлюзу самостійно списує токени для вхідних клієнтських запитів за кілька мікросекунд без міжсерверних блокувань. Якщо локальний запас вичерпується на 80%, шлюз превентивно надсилає наступний асинхронний запит `AcquireLease`, запобігаючи зупинці обслуговування трафіку.

```protobuf
syntax = "proto3";

package distributed.quota.v1;

option go_package = "github.com/courses/quota/v1;quotav1";

// Сервіс координації розподілених квот та лізингу
service QuotaService {
    // Асинхронний запит пачки токенів для локального бакета шлюзу
    rpc AcquireLease (AcquireLeaseRequest) returns (AcquireLeaseResponse);

    // Звітування про фактично витрачені токени та повернення невикористаного залишку
    rpc ReportUsage (ReportUsageRequest) returns (ReportUsageResponse);

    // Синхронна атомарна перевірка для критичних операцій (Fail-Closed)
    rpc CheckQuota (CheckQuotaRequest) returns (CheckQuotaResponse);
}

// Опис дескриптора орендаря та типу ресурсу
message QuotaDescriptor {
    string tenant_id = 1;        // Ідентифікатор організації / клієнта
    string resource_type = 2;     // Тип ресурсу: "requests", "cpu_ms", "egress_bytes"
    string tier = 3;              // Рівень тарифу: "enterprise", "standard", "free"
    map<string, string> labels = 4; // Додаткові мітки (маршрут, HTTP-метод, регіон)
}

message AcquireLeaseRequest {
    QuotaDescriptor descriptor = 1;
    uint32 requested_tokens = 2;  // Бажаний обсяг пачки токенів (Batch Size)
    uint32 lease_duration_ms = 3; // Бажана тривалість оренди у мілісекундах
    string gateway_instance_id = 4; // Унікальний ID інстансу шлюзу
}

message AcquireLeaseResponse {
    enum Status {
        STATUS_UNSPECIFIED = 0;
        GRANTED = 1;              // Квоту надано в повному обсязі
        PARTIALLY_GRANTED = 2;    // Надано менше токенів через дефіцит ресурсу
        DENIED_EXHAUSTED = 3;     // Квоту вичерпано на рівні організації
        DENIED_RATE_LIMITED = 4;  // Перевищено пікову інтенсивність (Burst Cap)
    }

    Status status = 1;
    uint32 granted_tokens = 2;    // Фактично виділена кількість токенів
    uint32 ttl_ms = 3;            // Дійсний час життя оренди (Time-To-Live)
    int64 reset_timestamp_epoch_ms = 4; // Момент повного оновлення глобальної квоти
    uint32 backoff_hint_ms = 5;   // Рекомендована пауза перед наступним запитом лізингу
}

message ReportUsageRequest {
    QuotaDescriptor descriptor = 1;
    string gateway_instance_id = 2;
    uint32 consumed_tokens = 3;   // Кількість успішно списаних токенів
    uint32 unused_tokens = 4;     // Невикористаний залишок для повернення в глобальний пул
}

message ReportUsageResponse {
    bool acknowledged = 1;
}

message CheckQuotaRequest {
    QuotaDescriptor descriptor = 1;
    uint32 cost = 2;              // Вартість поточної операції (за замовчуванням 1)
}

message CheckQuotaResponse {
    bool allowed = 1;
    uint32 remaining_tokens = 2;
    uint32 limit = 3;
    int64 reset_duration_ms = 4;
}
```

### Семантика статусів відповіді сервісу квот

Протокол лізингу підтримує п'ять станів відповіді, які визначають поведінку шлюзу:
* `GRANTED`: координатор виділив повну запитану кількість токенів. Шлюз поповнює локальний бакет і продовжує пропускати трафік без обмежень.
* `PARTIALLY_GRANTED`: глобальна квота орендаря майже вичерпана, тому координатор виділив лише частину запитаної суми. Шлюз приймає залишок і скорочує інтервал наступного оновлення.
* `DENIED_EXHAUSTED`: ліміт тарифного плану повністю вичерпано за поточний період. Шлюз негайно переходить у режим швидкого відхилення (Fail-Fast), повертаючи клієнту HTTP 429 з розрахунковим часом скидання лічильника.
* `DENIED_RATE_LIMITED`: клієнт перевищив допустиму пікову інтенсивність сплеску (Burst Rate), навіть якщо його сумарна місячна або годинна квота ще не вичерпана.

## 2. HTTP-заголовки квотування стандарту IETF

Для забезпечення прозорості та детермінованої поведінки клієнтських застосунків шлюзи API транслюють стан лімітів у кожній відповіді за допомогою заголовків робочої групи IETF (`RateLimit-Fields`):

| Заголовок | Тип значення | Опис та семантика |
|:---|:---|:---|
| `RateLimit-Limit` | `Integer` | Загальний ліміт квоти у поточному вікні часу (наприклад, `1000`). |
| `RateLimit-Remaining` | `Integer` | Кількість доступних токенів, що залишилися до кінця вікна (наприклад, `42`). |
| `RateLimit-Reset` | `Integer` | Кількість секунд до повного скидання лічильника та відновлення квоти. |
| `RateLimit-Policy` | `String` | Опис застосованої політики: `1000;w=60;burst=200;quota="requests"`. |
| `Retry-After` | `Integer` / `HTTP-Date` | Обов'язковий заголовок при статусі `429`: час очікування в секундах перед повторною спробою. |

### Приклад успішної відповіді (HTTP 200 OK)
```http
HTTP/1.1 200 OK
Content-Type: application/json
RateLimit-Limit: 1000
RateLimit-Remaining: 842
RateLimit-Reset: 18
RateLimit-Policy: 1000;w=60
```

### Приклад відхилення через вичерпання квоти (HTTP 429 Too Many Requests)
```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/problem+json
Retry-After: 12
RateLimit-Limit: 1000
RateLimit-Remaining: 0
RateLimit-Reset: 12
RateLimit-Policy: 1000;w=60

{
  "type": "https://api.example.com/errors/quota-exceeded",
  "title": "Tenant Quota Exceeded",
  "status": 429,
  "detail": "Організація 'tenant-941' вичерпала ліміт 1000 RPS для тарифного плану 'Standard'.",
  "instance": "/v1/payments/charge",
  "retry_after_seconds": 12,
  "tenant_id": "tenant-941",
  "resource": "requests_per_minute"
}
```

Клієнтські SDK (наприклад, gRPC client interceptors або HTTP client middleware) зобов'язані парсити заголовок `Retry-After` і автоматично ставити виклики на паузу, застосовуючи експоненційний відступ з випадковим джитером для запобігання шторму повторних спроб (Retry Storm).

## 3. Атомарний Lua-скрипт для Redis (Sliding Window & Token Bucket)

Для централізованого обліку квот у високошвидкісному сховищі Redis використовується Lua-скрипт. Виконання логіки всередині рушія Redis гарантує повну атомарність операцій перевірки та списання: між моментом читання залишку та його декрементом жоден інший шлюз не зможе втрутитися і спричинити стан гонитви (Race Condition).

Скрипт поєднує алгоритм Token Bucket із ковзним вікном, автоматично нараховуючи токени відповідно до часу, що минув з попереднього запиту:

```lua
-- KEYS[1]: Ключ бакета орендаря (наприклад, "quota:tenant_123:requests")
-- ARGV[1]: Максимальна місткість бакета (Max Tokens / Capacity)
-- ARGV[2]: Швидкість поповнення (Refill Rate, токенів на секунду)
-- ARGV[3]: Поточний Unix-час у мілісекундах
-- ARGV[4]: Кількість запитуваних токенів (Requested Tokens)

local bucket_key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now_ms = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

-- Зчитуємо поточний стан бакета (наявні токени та час останнього оновлення)
local data = redis.call("HMGET", bucket_key, "tokens", "last_updated_ms")
local current_tokens = tonumber(data[1])
local last_updated_ms = tonumber(data[2])

if current_tokens == nil then
    -- Перший запит: ініціалізуємо бакет повним обсягом
    current_tokens = capacity
    last_updated_ms = now_ms
else
    -- Розраховуємо кількість токенів, накопичених за час простою
    local elapsed_seconds = math.max(0, (now_ms - last_updated_ms) / 1000.0)
    local generated_tokens = elapsed_seconds * refill_rate
    current_tokens = math.min(capacity, current_tokens + generated_tokens)
    last_updated_ms = now_ms
end

-- Перевіряємо, чи достатньо токенів для задоволення запиту
local allowed = 0
local remaining = current_tokens
local retry_after_ms = 0

if current_tokens >= requested then
    allowed = 1
    current_tokens = current_tokens - requested
    remaining = current_tokens
else
    allowed = 0
    local missing_tokens = requested - current_tokens
    retry_after_ms = math.ceil((missing_tokens / refill_rate) * 1000.0)
end

-- Зберігаємо оновлений стан із TTL (подвійний час заповнення для автоочищення пам'яті)
local ttl_seconds = math.ceil((capacity / refill_rate) * 2)
redis.call("HMSET", bucket_key, "tokens", current_tokens, "last_updated_ms", last_updated_ms)
redis.call("EXPIRE", bucket_key, math.max(3600, ttl_seconds))

-- Повертаємо: [чи дозволено (1/0), залишок токенів, час очікування в мс]
return { allowed, math.floor(remaining), retry_after_ms }
```

### Розрахунок пам'яті та життєвого циклу ключів у Redis

Кожен активний орендар займає в Redis структуру `Hash` розміром приблизно 120 байтів. Для системи з 1 000 000 орендарів загальний обсяг оперативної пам'яті під лічильники квот становить близько 120 Мегабайтів. Команда `EXPIRE` автоматично вичищає ключі неактивних клієнтів, запобігаючи неконтрольованому витоку пам'яті.

## 4. Конфігурація фільтра Rate Limit у проксі Envoy

Нижче наведено робочий фрагмент конфігурації фільтра `envoy.filters.http.ratelimit` для інтеграції сервісу розподіленого квотування в інфраструктуру Service Mesh:

```yaml
static_resources:
  listeners:
  - name: ingress_http_listener
    address:
      socket_address: { address: 0.0.0.0, port_value: 8080 }
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          stat_prefix: ingress_http
          route_config:
            name: local_route
            virtual_hosts:
            - name: api_service
              domains: ["*"]
              routes:
              - match: { prefix: "/v1/" }
                route:
                  cluster: backend_service
                  rate_limits:
                  - actions:
                    - request_headers:
                        header_name: "X-Tenant-ID"
                        descriptor_key: "tenant_id"
                    - request_headers:
                        header_name: ":method"
                        descriptor_key: "http_method"
          http_filters:
          - name: envoy.filters.http.ratelimit
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.ratelimit.v3.RateLimit
              domain: edge_rate_limits
              timeout: 0.05s # Жорсткий таймаут звернення до квотера (50 мс)
              failure_mode_deny: false # Режим Fail-Open при збої сервісу квот
              rate_limit_service:
                grpc_service:
                  envoy_grpc:
                    cluster_name: global_quota_service_cluster
                transport_api_version: V3
          - name: envoy.filters.http.router
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
```

## 5. Механізми лізингу, телеметрія та компроміси точності

Процес асинхронного лізингу базується на циклічній взаємодії між шлюзом та координатором:

1. **Ініціалізація та первинне завантаження:** під час запуску інстансу шлюзу локальний кеш квот порожній. Перший вхідний запит орендаря ініціює асинхронний виклик `AcquireLease` з розміром пачки за замовчуванням (наприклад, 100 токенів).
2. **Локальне декрементування та префетчинг:** шлюз обслуговує наступні виклики клієнта зі свого локального пулу. Коли кількість доступних токенів опускається нижче порогового значення (Low Watermark = 20% від розміру пачки), фоновий потік надсилає новий виклик `AcquireLease`. Завдяки цьому клієнт не стикається з мережевими затримками.
3. **Повернення невикористаного залишку (Reconciliation):** якщо клієнт раптово припинив надсилати запити, орендовані токени не блокуються назавжди. Після закінчення таймера оренди (`lease_duration_ms`) шлюз автоматично повертає залишок координатору через `ReportUsage`, роблячи ці токени доступними для інших інстансів шлюзів у сусідніх зонах доступності.
4. **Захист від розсинхронізації часу (Clock Skew Mitigation):** усі часові інтервали оренди передаються як відносні тривалості (TTL у мілісекундах), а не абсолютні мітки часу хоста. Це захищає систему від розбіжностей системних годинників серверів за протоколом NTP.

### Метрики Prometheus для моніторингу квотування

Для безперервного спостереження за поведінкою системи рекомендується збирати такі стандартні метрики:
* `quota_leases_acquired_total{tenant, status}`: кількість успішних та відхилених запитів на оренду токенів.
* `quota_local_tokens_available{tenant}`: поточний миттєвий залишок токенів у локальній пам'яті шлюзу.
* `quota_throttled_requests_total{tenant, route}`: кількість запитів клієнтів, відхилених з кодом HTTP 429.
* `quota_lease_rpc_duration_seconds`: гістограма затримок взаємодії між шлюзом та центральним Redis/gRPC квотером.

| Параметр | Рекомендоване значення | Опис інженерного впливу |
|:---|:---|:---|
| `LeaseDuration` | `200–1000 мс` | Тривалість локальної оренди токенів. Менше значення підвищує точність обліку, більше — кардинально знижує навантаження на Redis. |
| `BatchSize` | `50–500 токенів` | Розмір пачки токенів, що резервується шлюзом за один RPC-виклик до координатора. |
| `BurstMultiplier` | `1.2–2.0` | Коефіцієнт пікової ємності бакета відносно номінального RPS для поглинання короткочасних мікросплесків без помилок 429. |
| `FailureMode` | `Fail-Open / Fail-Closed` | Поведінка шлюзу при втраті зв'язку з координатором квот (пропуск штатного трафіку чи жорстке блокування нових викликів). |
| `CostHeader` | `X-Request-Cost` | Опціональний заголовок від бекенду для апостеріорного списання токенів за важкі аналітичні операції. |

Вибір між режимами `Fail-Open` та `Fail-Closed` є фундаментальним бізнес-рішенням: для публічних вебсервісів електронної комерції обирають `Fail-Open`, оскільки втрата замовлень через збій кешу квот неприпустима; натомість для платної генерації тексту в LLM-сервісах або платіжних шлюзах застосовують `Fail-Closed`, захищаючи компанію від мільйонних фінансових перевитрат.
