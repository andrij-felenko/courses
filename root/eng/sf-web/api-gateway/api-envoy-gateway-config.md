# 📋 Декларативна конфігурація Envoy та Kubernetes Gateway API

Цей довідник містить вичерпну технічну специфікацію структури полів, інваріантів, конфігураційних моделей та механізмів конвеєра фільтрів сучасного API-шлюзу на базі стандарту **Kubernetes Gateway API** та нативного рушія **Envoy Proxy**. Довідник описує повний контракт взаємодії між інфраструктурною площиною та прикладними сервісами, правила L7-маршрутизації, захисту від перевантаження, верифікації токенів, керування політиками CORS, інтеграції WAF, налаштування розподіленого трейсингу та аналізу діагностичних статусів.

---

## Архітектурна модель Kubernetes Gateway API

Стандарт Gateway API розв'язує фундаментальну проблему класичного ресурсу Kubernetes Ingress — небезпечне змішування інфраструктурних параметрів (мережеві інтерфейси, порти, TLS-сертифікати, IP-адреси) із прикладними правилами маршрутизації окремих команд розробки.

У специфікації Gateway API обов'язки чітко розмежовано між трьома системними ролями:

1. **Провайдер інфраструктури (Infrastructure Provider):** створює ресурс `GatewayClass`, який визначає тип контролера (наприклад, `envoy-gateway`, `kong`, `traefik`) та глобальні системні параметри середовища.
2. **Інфраструктурний інженер (Platform / Cluster Operator):** створює ресурс `Gateway`, виділяючи статичні IP-адреси, відкриваючи мережеві порти (`80`, `443`), підключаючи Secret-об'єкти з TLS-сертифікатами та налаштовуючи глобальні політики безпеки й просторів імен.
3. **Команда продуктового сервісу (Application Developer):** створює ресурс `HTTPRoute` (або `GRPCRoute`, `TCPRoute`), який декларує правила маршрутизації шляхів, модифікацію заголовків, таймаути та вагові коефіцієнти для канаркового розгортання, прив'язуючись до батьківського шлюзу за допомогою селектора `parentRefs`.

```
  [ Інфраструктурний інженер ]          [ Команда продуктового сервісу ]
               │                                       │
               ▼                                       ▼
  ┌─────────────────────────┐             ┌─────────────────────────┐
  │         Gateway         │◄────────────│        HTTPRoute        │
  │ • Слухачі: 80, 443      │  Прив'язка  │ • Префікс: /api/v1/orders│
  │ • TLS-сертифікати       │  селектором │ • Фільтри заголовків    │
  │ • Публічна IP-адреса    │ parentRefs  │ • Цільові мікросервіси  │
  └─────────────────────────┘             └─────────────────────────┘
```

---

## Специфікація ресурсу `Gateway`

Ресурс `Gateway` описує фізичну або віртуальну точку присутності шлюзу на мережевому периметрі:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: edge-gateway
  namespace: gateway-infra
spec:
  gatewayClassName: envoy-gateway
  listeners:
    - name: https-api
      protocol: HTTPS
      port: 443
      hostname: "api.example.com"
      tls:
        mode: Terminate
        certificateRefs:
          - group: ""
            kind: Secret
            name: api-example-tls-cert
      allowedRoutes:
        namespaces:
          from: Selector
          selector:
            matchLabels:
              gateway-access: "true"
    - name: http-redirect
      protocol: HTTP
      port: 80
      hostname: "api.example.com"
      allowedRoutes:
        namespaces:
          from: Same
```

### Детальний опис полів ресурсу `Gateway`

| Поле | Тип | Обов'язкове | Призначення, інваріанти та поведінка |
|---|---|---|---|
| `spec.gatewayClassName` | `string` | Так | Назва зареєстрованого в кластері класу `GatewayClass`. Контролер шлюзу відстежує лише ресурси зі своїм іменем класу. |
| `spec.listeners[]` | `list` | Так | Список незалежних мережевих слухачів (порт + протокол + правила TLS). |
| `listeners[].name` | `string` | Так | Унікальне ім'я слухача в межах даного шлюзу (використовується в `sectionName` маршрутів). |
| `listeners[].port` | `integer` | Так | Порт прослуховування (`1..65535`). Зазвичай `443` для захищеного трафіку та `80` для редиректу. |
| `listeners[].protocol` | `enum` | Так | Підтримувані протоколи: `HTTP`, `HTTPS`, `TLS`, `TCP`, `UDP`. Для `HTTPS` обов'язковий блок `tls`. |
| `listeners[].hostname` | `string` | Ні | Точне або wildcard доменне ім'я (наприклад, `*.example.com`). Запити з іншим заголовком `Host`/`:authority` відхиляються на рівні L7. |
| `listeners[].tls.mode` | `enum` | Для HTTPS | `Terminate` — шлюз розшифровує TLS за допомогою наданого сертифіката; `Passthrough` — шлюз пересилає зашифрований потік байтів без розшифрування за протоколом SNI (L4 проксіювання). |
| `listeners[].tls.certificateRefs` | `list` | Для HTTPS | Посилання на Secret у тому самому просторі імен, що містить `tls.crt` та `tls.key`. |
| `listeners[].allowedRoutes` | `object` | Ні | Політика безпеки, що визначає, які простори імен мають право прив'язувати маршрути до цього слухача. Можливі значення: `from: All` (усі простори), `from: Same` (лише той самий простір), `from: Selector` (простори імен з відповідними мітками). |

---

## Специфікація ресурсу `HTTPRoute`

Ресурс `HTTPRoute` декларує правила зіставлення вхідного HTTP-трафіку, його модифікації та пересилання на конкретні бекенд-сервіси:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: orders-v1-route
  namespace: production-orders
spec:
  parentRefs:
    - name: edge-gateway
      namespace: gateway-infra
      sectionName: https-api
  hostnames:
    - "api.example.com"
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /api/v1/orders
          method: POST
          headers:
            - type: Exact
              name: Content-Type
              value: application/json
      filters:
        - type: RequestHeaderModifier
          requestHeaderModifier:
            set:
              - name: X-Gateway-Origin
                value: k8s-edge-envoy
            remove:
              - X-Untrusted-Client-Header
              - X-Internal-Debug-Bypass
        - type: URLRewrite
          urlRewrite:
            path:
              type: ReplacePrefixMatch
              replacePrefixMatch: /internal/v1/orders
      backendRefs:
        - name: orders-backend-stable
          port: 8080
          weight: 90
        - name: orders-backend-canary
          port: 8080
          weight: 10
      timeouts:
        request: 500ms
        backendRequest: 350ms
```

### Детальний опис полів ресурсу `HTTPRoute`

| Поле / Блок | Тип | Опис, правила валідації та навантаження |
|---|---|---|
| `spec.parentRefs[]` | `list` | Список шлюзів, до яких підключається даний маршрут. Вказує `name`, `namespace` та необов'язковий `sectionName` (конкретний слухач). |
| `spec.hostnames[]` | `list` | Список віртуальних хостів. Повинен бути підмножиною або збігатися з `hostname` батьківського слухача. |
| `rules[].matches[]` | `list` | Список умов збігу (об'єднуються логічним «АБО» між елементами списку, та логічним «І» всередині одного блоку збігу). |
| `matches[].path.type` | `enum` | `PathPrefix` — збіг за префіксом шляху з урахуванням роздільника `/` (наприклад, `/api` збігається з `/api/v1`, але не з `/apidoc`); `Exact` — точний посимвольний збіг. |
| `matches[].method` | `enum` | Фільтрація за HTTP-методом: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `HEAD`, `OPTIONS`. |
| `matches[].headers[]` | `list` | Зіставлення за заголовками (`Exact` або `RegularExpression`). Заголовки нормалізуються до нижнього регістру. |
| `rules[].filters[]` | `list` | Ланцюжок фільтрів модифікації трафіку перед відправкою на бекенд. |
| `filters[].type` | `enum` | Тип фільтра: `RequestHeaderModifier` (додавання/видалення заголовків), `ResponseHeaderModifier` (модифікація заголовків відповіді), `URLRewrite` (переписування шляху або хоста), `RequestMirror` (тіньове копіювання трафіку на тестовий сервіс). |
| `rules[].backendRefs[]` | `list` | Список цільових Kubernetes Service. Поле `weight` задає пропорцію трафіку для канаркових або синьо-зелених розгортань (наприклад, ваги 90 і 10 означають, що 10% запитів отримає canary-сервіс). |
| `rules[].timeouts.request` | `duration` | Повний клієнтський таймаут запиту включно з усіма внутрішніми повторами (retries). Якщо бекенди не вклалися в цей час, шлюз повертає клієнту `504 Gateway Timeout`. |
| `rules[].timeouts.backendRequest` | `duration` | Таймаут одного індивідуального звернення до конкретного поду бекенда перед здійсненням наступної спроби. |

---

## Нативна конфігурація фільтрів Envoy Proxy

Для систем, що конфігурують Envoy напряму через Control Plane (gRPC xDS API) або локальні YAML-маніфести, ланцюжок фільтрів конфігурується в блоці `http_connection_manager`.

### 1. Фільтр перевірки автентифікації JWT (`jwt_authn`)

Фільтр виконує локальну перевірку криптографічних підписів токенів JWT без виконання синхронних викликів на кожен запит. Відкриті ключі постачальника ідентифікації (JWKS) кешуються в пам'яті процесу та автоматично оновлюються у фоновому режимі:

```yaml
- name: envoy.filters.http.jwt_authn
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.jwt_authn.v3.JwtAuthentication
    providers:
      corporate_idp:
        issuer: https://identity.example.com/oauth2/v1
        audiences:
          - "https://api.example.com"
          - "https://internal-services.example.com"
        remote_jwks:
          http_uri:
            uri: https://identity.example.com/oauth2/v1/keys
            cluster: jwks_idp_cluster
            timeout: 1.5s
          cache_duration: 600s
          async_fetch:
            fast_listener: true
        payload_in_metadata: verified_jwt_claims
        from_headers:
          - name: Authorization
            value_prefix: "Bearer "
        pad_forward_payload_header: "X-Jwt-Payload-Base64"
    rules:
      - match:
          prefix: /api/v1/public/
        # Публічні шляхи не вимагають токена
      - match:
          prefix: /api/v1/
        requires:
          provider_name: corporate_idp
```

### 2. Фільтр захисту від перевантаження (Local Rate Limiting)

Локальний лімітер швидкості захищає шлюз від різких спалахів трафіку, використовуючи внутрішній лічильник Token Bucket на кожному робочому потоці без звернення до зовнішньої бази даних:

```yaml
- name: envoy.filters.http.local_ratelimit
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit
    stat_prefix: http_local_rate_limiter
    status:
      code: 429
    token_bucket:
      max_tokens: 10000
      tokens_per_fill: 2000
      fill_interval: 1s
    filter_enabled:
      runtime_key: local_rate_limit_enabled
      default_value:
        numerator: 100
        denominator: HUNDRED
    filter_enforced:
      runtime_key: local_rate_limit_enforced
      default_value:
        numerator: 100
        denominator: HUNDRED
    response_headers_to_add:
      - append_action: OVERWRITE_IF_EXISTS_OR_ADD
        header:
          key: Retry-After
          value: "1"
      - append_action: OVERWRITE_IF_EXISTS_OR_ADD
        header:
          key: X-RateLimit-Limit
          value: "2000"
```

### 3. Конфігурація пулу upstream-з'єднань та запобіжників (Circuit Breakers)

У конфігурації upstream-кластера Envoy задаються суворі ліміти ресурсів, які запобігають вичерпанню пам'яті та накопиченню каскадних черг при уповільненні бекенд-сервісу:

```yaml
clusters:
  - name: orders_cluster_v1
    connect_timeout: 0.25s
    type: STRICT_DNS
    dns_lookup_family: V4_ONLY
    lb_policy: ROUND_ROBIN
    typed_extension_protocol_options:
      envoy.extensions.upstreams.http.v3.HttpProtocolOptions:
        "@type": type.googleapis.com/envoy.extensions.upstreams.http.v3.HttpProtocolOptions
        explicit_http_config:
          http2_protocol_options:
            max_concurrent_streams: 100
    circuit_breakers:
      thresholds:
        - priority: DEFAULT
          max_connections: 1024       # Ліміт одночасних TCP-з'єднань до бекенда
          max_pending_requests: 128   # Черга запитів, що чекають на вільне з'єднання
          max_requests: 4096          # Максимум паралельних активних HTTP/2 запитів
          max_retries: 3              # Максимум одночасних повторних запитів
          track_remaining: true
    outlier_detection:
      consecutive_5xx: 5              # 5 помилок 5xx поспіль викидають інстанс із пулу
      interval: 10s                   # Інтервал аналізу статистики
      base_ejection_time: 30s         # Базовий час виключення несправного поду
      max_ejection_percent: 50        # Заборонено викидати більше 50% екземплярів
      enforcing_consecutive_5xx: 100  # 100% суворість застосування правила
```

### 4. Керування політиками CORS (Cross-Origin Resource Sharing)

Для забезпечення безпечного доступу односторінкових вебзастосунків (SPA) з різних доменів конфігурація шлюзу містить спеціалізований фільтр `cors`:

```yaml
- name: envoy.filters.http.cors
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.cors.v3.Cors
```

На рівні маршруту задаються правила обробки попередніх запитів (Preflight `OPTIONS`):
* `allow_origin_string_match`: список дозволених доменів (наприклад, `https://app.example.com`).
* `allow_methods`: перелік дозволених методів (`GET, POST, PUT, DELETE, OPTIONS`).
* `allow_headers`: дозволені клієнтські заголовки (`Authorization, Content-Type, X-Request-ID`).
* `expose_headers`: заголовки, які веббраузер дозволяє читати JavaScript-коду (`X-Correlation-ID, Retry-After`).
* `max_age`: час кешування попереднього запиту `OPTIONS` у браузері (типово `86400s`), що знімає навантаження зайвих перевірок.
* `allow_credentials`: булевий прапорець дозволу передачі сесійних кукі та авторизаційних заголовків.

### 5. Інтеграція Web Application Firewall (WAF) через WebAssembly (WASM)

Сучасні шлюзи на базі Envoy дозволяють вбудовувати правила перевірки трафіку на наявність сигнатур атак OWASP Top 10 (SQL-ін'єкції, міжсайтовий скриптінг XSS, Path Traversal) за допомогою скомпільованих WASM-модулів (наприклад, Coraza WAF):

```yaml
- name: envoy.filters.http.wasm
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.wasm.v3.Wasm
    config:
      name: coraza_waf
      root_id: coraza_root
      vm_config:
        runtime: envoy.wasm.runtime.v8
        code:
          local:
            filename: /etc/envoy/coraza_waf.wasm
      configuration:
        "@type": type.googleapis.com/google.protobuf.StringValue
        value: |
          SecRuleEngine On
          SecRequestBodyAccess On
          SecRule REQUEST_URI "@rx \.\./" "id:1001,phase:1,deny,status:403,msg:'Path traversal attempt'"
```

WASM-модуль виконується в ізольованій пісочниці всередині процесу Envoy, забезпечуючи високу швидкість фільтрації без викликів зовнішніх демонів.

### 6. Налаштування експорту розподіленого трейсингу (OpenTelemetry)

Для наскрізного моніторингу запитів у блоці `http_connection_manager` конфігурується модуль розподіленого трасування:

```yaml
tracing:
  provider:
    name: envoy.tracers.opentelemetry
    typed_config:
      "@type": type.googleapis.com/envoy.config.trace.v3.OpenTelemetryConfig
      grpc_service:
        envoy_grpc:
          cluster_name: otel_collector_cluster
        timeout: 0.25s
      service_name: api-edge-gateway
```

Шлюз автоматично зчитує вхідні заголовки `traceparent` та `tracestate` стандарту W3C Trace Context або створює новий кореневий Span із генерацією унікального ідентифікатора сліду (Trace ID), надсилаючи телеметрію до OpenTelemetry Collector через протокол gRPC.

---

## Діагностичні коди відповідей та прапорці Envoy

Коли шлюз відхиляє запит або отримує збій від внутрішнього бекенда, він генерує відповідний HTTP-статус та записує у внутрішній журнал структурований прапорець причини (Envoy Response Flags):

| HTTP-код | Назва | Прапорець Envoy | Джерело генерації та діагностична причина |
|---|---|---|---|
| **`400`** | `Bad Request` | `-` | Синтаксична помилка в HTTP-запиті клієнта, недійсний URI або непідтримуваний протокол. |
| **`401`** | `Unauthorized` | `JwtMissing / JwtExpired` | Запит не містить токена `Authorization` або підпис JWT не пройшов перевірку через JWKS. |
| **`403`** | `Forbidden` | `RBACAccessDenied` | Токен валідний, але набір ролей чи `scope` не надає прав доступу до даного маршруту. |
| **`404`** | `Not Found` | `NR` (No Route) | Жоден із зареєстрованих маршрутів не збігся за комбінацією `Host`, `Path` та `Headers`. |
| **`429`** | `Too Many Requests` | `RL` (Rate Limited) | Перевищено встановлений ліміт запитів (Token Bucket). Шлюз повертає заголовок `Retry-After`. |
| **`503`** | `Service Unavailable` | `UO` (Upstream Overflow) | Спрацював запобіжник: переповнено чергу `max_pending_requests` або всі бекенди викинуті Outlier Detection. |
| **`503`** | `Service Unavailable` | `UF` (Upstream Failure) | Помилка з'єднання: відмова при TCP-рукостисканні з бекендом (Connection Refused). |
| **`503`** | `Service Unavailable` | `UH` (No Healthy Host) | Усі екземпляри бекенда в кластері позначені як нездорові за результатами Health Check. |
| **`504`** | `Gateway Timeout` | `UT` (Upstream Timeout) | Бекенд не відповів за час `request_timeout` або `backendRequestTimeout`. |
| **`504`** | `Gateway Timeout` | `DC` (Downstream Cancel) | Клієнт розірвав з'єднання до того, як внутрішній сервіс встиг повернути відповідь. |
| **`504`** | `Gateway Timeout` | `URX` (Retry Limit Exceeded) | Вичерпано ліміт повторних спроб (`max_retries`) без отримання успішної відповіді. |

---

## Інженерний чеклист діагностики шлюзу в продакшені

Під час розслідування інцидентів на шлюзі інженери використовують адміністративний інтерфейс Envoy (типово на порту `:15000` або через утиліти командного рядка):

1. **Перевірка стану маршрутизації та адрес бекендів:**
   Виклик `GET /config_dump?include_eds` вивантажує повний зліпок поточної конфігурації активних маршрутів, ланцюжків фільтрів та динамічних IP-адрес ендпоінтів, отриманих від Kubernetes API. Якщо запит повертає `404 NR`, необхідно звірити точність регулярних виразів та наявність слешів у префіксі маршруту.
2. **Перевірка стану запобіжників та черг:**
   Виклик `GET /stats?filter=circuit_breakers` відображає лічильники `upstream_cx_overflow` (відхилені з'єднання через перевищення ліміту) та `upstream_rq_pending_overflow` (переповнені черги запитів). Ненульові значення свідчать про те, що бекенд-сервіс не справляється з навантаженням і потребує масштабування.
3. **Аналіз прапорців у структурованих логах:**
   Пошук за прапорцями `UF` (проблема мережевої зв'язності або падіння процесу поду) та `UT` (зависання запитів у базі даних бекенда) дозволяє за секунди локалізувати джерело проблеми без необхідності читати гігабайти прикладних логів сервісів.
4. **Контроль витоків дескрипторів сокетів:**
   Метрика `server.allocated_connections` та `server.total_connections` показує кількість активних сесій клієнтів. Якщо графік постійно росте без повернення до базового рівня, це свідчить про зависання клієнтів через відсутність таймера `idle_timeout`.
