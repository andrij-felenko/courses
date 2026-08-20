# 📋 Контракт конфігурації Envoy: L4 filter chain проти L7 route table

У сучасному стеку розподілених систем Envoy Proxy є стандартом де-факто для обох рівнів балансування. Архітектура Envoy базується на конвеєрі обробки даних, де слухачі (`listeners`) приймають вхідні з'єднання, ланцюжки фільтрів (`filter_chains`) поетапно обробляють байти або кадри, а кластери бекендів (`clusters`) керують пулами з'єднань із кінцевими вузлами.

Цей довідник визначає контракт між декларативною конфігурацією Envoy та режимами обробки трафіку: на транспортному рівні (L4) через фільтр `tcp_proxy` та на прикладному рівні (L7) через `http_connection_manager`.

### Життєвий цикл обробки трафіку в Envoy

Коли ядро операційної системи передає новий сокет процесу Envoy, обробка проходить послідовний ланцюжок фаз:

1. **Фаза слухача (Listener Phase):** сокет приймається робітником (Worker Thread). На цьому етапі можуть спрацьовувати фільтри слухача (`listener_filters`), наприклад `tls_inspector`, який вичитує початкові байти пакета `ClientHello` для визначення Server Name Indication (SNI) та узгодженого протоколу ALPN без розшифрування сесії.
2. **Селекція ланцюжка фільтрів (Filter Chain Matching):** на основі IP-адреси джерела, порту, SNI або протоколу обирається конкретний ланцюжок `filter_chains`.
3. **Мережева обробка (Network Filters):**
   * У режимі L4 активується фільтр `envoy.filters.network.tcp_proxy`, який безпосередньо відкриває потік до цільового кластера.
   * У режимі L7 активується `envoy.filters.network.http_connection_manager`, який бере на себе повну термінацію TLS, ініціалізує HTTP-парсер відповідної версії (HTTP/1.1, HTTP/2 або HTTP/3) і запускає підконвеєр HTTP-фільтрів.

---

### Специфікація L4: Мережевий фільтр `tcp_proxy`

Фільтр `envoy.filters.network.tcp_proxy` забезпечує прозоре перенаправлення TCP-потоків без розбору протоколу прикладного рівня та без модифікації корисного навантаження.

```yaml
static_resources:
  listeners:
  - name: l4_tcp_listener
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 10000
    listener_filters:
    - name: envoy.filters.listener.tls_inspector
      typed_config:
        "@type": type.googleapis.com/envoy.extensions.filters.listener.tls_inspector.v3.TlsInspector
    filter_chains:
    - filter_chain_match:
        server_names: ["db-replica.example.com"]
      filters:
      - name: envoy.filters.network.tcp_proxy
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.tcp_proxy.v3.TcpProxy
          stat_prefix: ingress_tcp_db
          cluster: backend_database_cluster
          idle_timeout: 300s
          max_connect_attempts: 3
  clusters:
  - name: backend_database_cluster
    connect_timeout: 0.25s
    type: STRICT_DNS
    lb_policy: ROUND_ROBIN
    load_assignment:
      cluster_name: backend_database_cluster
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: db-primary.internal
                port_value: 5432
```

#### Параметри контракту L4 `tcp_proxy`:

| Поле | Тип | Обов'язкове | Призначення та поведінка |
| :--- | :--- | :--- | :--- |
| `stat_prefix` | `string` | Так | Префікс для метрик телеметрії (`downstream_cx_total`, `downstream_flow_control_paused`). |
| `cluster` | `string` | Так | Назва цільового кластера в `static_resources.clusters`, куди перенаправляється TCP-потік. |
| `idle_timeout` | `Duration` | Ні | Час неактивності з'єднання до примусового закриття (за замовчуванням: `1h`). |
| `max_connect_attempts`| `uint32` | Ні | Кількість спроб встановити TCP-з'єднання з бекендом у разі відмови (за замовчуванням: `1`). |
| `tunneling_config` | `Object` | Ні | Опціональне загортання TCP-потоку в HTTP CONNECT тунель. |

#### Інваріанти та поведінка фільтра `tcp_proxy`:
* **Симетрія потоку:** фільтр організовує пряму трансляцію подій `read` з сокета клієнта в подію `write` сокета бекенда. Якщо буфер відправки бекенда заповнюється, Envoy вимикає подію `POLLIN` на клієнтському сокеті (реалізація зворотного тиску, backpressure).
* **Недоступність бекендів:** якщо під час встановлення зв'язку всі вузли кластера не відповідають, Envoy негайно закриває клієнтський сокет пакетом `TCP RST` або надсилає `FIN`, не генеруючи жодних текстових відповідей.
* **Трансляція напівзакриття:** надходження клієнтського пакета `FIN` транслюється у виклик `shutdown(SHUT_WR)` на висхідному з'єднанні.
* **Пропускна здатність та оптимізація:** фільтр не виконує динамічного виділення пам'яті під час перекачування даних між сокетами, використовуючи попередньо виділені буферні зрізи (Buffer Slices).

---

### Специфікація L7: Фільтр `http_connection_manager`

Фільтр `envoy.filters.network.http_connection_manager` повністю термінує транспортні з'єднання (включаючи TLS), демультиплексує потоки HTTP/1.1, HTTP/2 та HTTP/3 і маршрутизує окремі HTTP-запити на основі заголовків, методів та шляхів.

```yaml
static_resources:
  listeners:
  - name: l7_http_listener
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 8080
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          stat_prefix: ingress_http
          codec_type: AUTO
          route_config:
            name: local_route
            virtual_hosts:
            - name: backend_vhost
              domains: ["api.example.com"]
              routes:
              - match:
                  prefix: "/api/v1/orders"
                route:
                  cluster: order_service_cluster
                  timeout: 2.5s
                  retry_policy:
                    retry_on: "5xx,connect-failure,refused-stream"
                    num_retries: 3
                    retry_back_off:
                      base_interval: 25ms
                      max_interval: 250ms
              - match:
                  prefix: "/static"
                route:
                  cluster: static_assets_cluster
                  timeout: 10s
          http_filters:
          - name: envoy.filters.http.router
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
```

#### Параметри контракту маршрутизації L7:

| Поле | Тип | Обов'язкове | Призначення та поведінка |
| :--- | :--- | :--- | :--- |
| `codec_type` | `Enum` | Ні | Режим декодування: `AUTO`, `HTTP1`, `HTTP2`, `HTTP3`. `AUTO` використовує ALPN або початкові байти. |
| `virtual_hosts` | `Array` | Так | Список логічних хостів, зіставлених за заголовком `Host` або `:authority`. |
| `routes.match` | `Object` | Так | Правила зіставлення: `prefix`, `path` (exact), `safe_regex`, `headers`, `query_parameters`. |
| `routes.route.cluster`| `string` | Так | Цільовий пул серверів для запитів, що відповідають правилу збігу. |
| `routes.route.timeout`| `Duration` | Ні | Наскрізний таймаут очікування відповіді від бекенда; повертає `504 Gateway Timeout`. |
| `retry_policy` | `Object` | Ні | Автоматичний повтор запитів за вказаними умовами (`5xx`, `retriable-status-codes`, `reset`). |

#### Механізм зіставлення маршрутів (Route Matching Engine):
1. **Зіставлення віртуального хоста:** Envoy перевіряє значення заголовка `:authority` (для HTTP/2 та HTTP/3) або `Host` (для HTTP/1.1) проти масиву шаблонів `domains`. Підтримуються точні збіги (`api.example.com`), маски ліворуч (`*.example.com`) та маски праворуч (`api.*`). Якщо збігу немає, використовується віртуальний хост із доменом `*` (якщо він оголошений), або повертається статус `404 Not Found`.
2. **Лінійний обхід таблиці маршрутів:** усередині знайденого віртуального хоста правила в списку `routes` перевіряються строго зверху вниз до першого збігу. Тому специфічні шляхи (наприклад, `/api/v1/orders/export`) обов'язково розміщують вище за загальні префікси (`/api/v1`).
3. **Обчислення прапорців відповіді та діагностика:** якщо запит не вдалося відправити до бекенда, Envoy генерує локальну відповідь зі спеціальними кодами причин (Response Flags):
   * `NR` (No Route Configured) — жоден маршрут не збігся із запитом.
   * `UH` (No Healthy Upstream) — у цільовому кластері всі бекенди позначені як непрацездатні за результатами Health Checks.
   * `UT` (Upstream Request Timeout) — висхідний сервер не вклався у ліміт `route.timeout`.
   * `UF` (Upstream Connection Failure) — збій встановлення TCP-з'єднання або відмова під час TLS-рукостискання з бекендом.
   * `UO` (Upstream Overflow) — перевищено ліміт пулу з'єднань або ліміт черги запитів (Circuit Breaking).

---

### Контракт запобіжників (Circuit Breaking) та відсікання вузлів (Outlier Detection)

На рівні L7 Envoy надає точний контракт обмеження навантаження на кластер бекендів:

```yaml
clusters:
- name: order_service_cluster
  connect_timeout: 0.5s
  type: EDS
  circuit_breakers:
    thresholds:
    - priority: DEFAULT
      max_connections: 1024
      max_pending_requests: 100
      max_requests: 4096
      max_retries: 3
  outlier_detection:
    consecutive_5xx: 5
    interval: 10s
    base_ejection_time: 30s
    max_ejection_percent: 50
```

#### Інваріанти поведінки запобіжників:
* `max_connections`: гранична кількість відкритих TCP-з'єднань Envoy з екземплярами цього кластера.
* `max_pending_requests`: максимальна довжина черги запитів, що очікують на вільне з'єднання в пулі; при перевищенні Envoy негайно повертає клієнту статус `503 Service Unavailable` з прапорцем `UO`.
* `consecutive_5xx`: якщо окремий вузол кластера повертає 5 послідовних відповідей із кодами 5xx, Envoy виключає його з пулу активної ротації на час `base_ejection_time`.
* `max_ejection_percent`: захист від каскадного колапсу; навіть за масових збоїв Envoy ніколи не виключить більше 50% вузлів кластера, щоб уникнути перевантаження вцілілих серверів.

---

### Контракт активних перевірок здоров'я (Health Checking)

Envoy підтримує періодичне опитування цільових вузлів на обох рівнях, проте семантика суттєво різниться:
* **L4 Health Check:** надсилає простий TCP-пінг або перевіряє успішність триетапного рукостискання (`SYN -> SYN-ACK -> ACK`). Цей метод виявляє лише падіння процесу або мережеву недоступність, але не бачить внутрішніх глухих кутів програми (deadlocks).
* **L7 Health Check:** відправляє повноцінний запит `GET /healthz` і перевіряє статус-код `200 OK`, наявність очікуваного тіла відповіді або статус готовності gRPC через протокол `grpc.health.v1.Health`. Якщо бекенд перевантажений і не може зв'язатися з базою даних, він повертає `503`, і Envoy вилучає його з балансування ще до того, як туди потраплять реальні клієнтські запити.

---

### Динамічне оновлення конфігурації через xDS API

У виробничих хмарних середовищах конфігурація Envoy рідко пишеться у вигляді статичних YAML-файлів. Натомість використовується протокол динамічного виявлення ресурсів (xDS), де площина керування (Control Plane) надсилає оновлення через gRPC-стріми:
* **LDS (Listener Discovery Service):** динамічне відкриття та закриття портів слухачів і зміна мережевих фільтрів.
* **RDS (Route Discovery Service):** миттєве оновлення таблиць маршрутизації L7 без перезавантаження сокетів і без розриву існуючих TCP-з'єднань.
* **CDS (Cluster Discovery Service):** динамічна реєстрація нових кластерів сервісів.
* **EDS (Endpoint Discovery Service):** постачання актуальних IP-адрес та портів мікросервісів у міру їхнього автомасштабування або рестарту в кластерах Kubernetes.

Завдяки відокремленню RDS та EDS від транспортного рівня, додавання нових серверів або зміна шляхів маршрутизації застосовуються за мілісекунди без жодної втрати наявних клієнтських сесій.

---

### Порівняльний контракт можливостей

| Можливість | Контракт L4 (`tcp_proxy`) | Контракт L7 (`http_connection_manager`) |
| :--- | :--- | :--- |
| **Одиниця маршрутизації** | Ціле TCP-з'єднання | Окремий HTTP-запит або gRPC-виклик |
| **Зіставлення (Matching)** | Лише IP-адреса, порт та SNI (TLS) | Шлях URI, метод, заголовки, Query-параметри, Cookies |
| **Трансформація даних** | Неможлива (байти незмінні) | Додавання/видалення заголовків, переписування URL |
| **Політика повторів (Retry)** | Неможлива на рівні окремого запиту | Автоматичний повтор невдалих HTTP 503/504 запитів |
| **Демультиплексування** | Відсутнє (усі потоки HTTP/2 йдуть на 1 вузол) | Розподіл кожного HTTP/2 потоку на окремий бекенд |
| **Коди помилок клієнту** | Розірвання з'єднання (`TCP RST` / `FIN`) | Детальні статуси `404`, `502`, `503`, `504` з JSON/HTML тілом |
| **Накладні витрати пам'яті** | ~2–4 КБ на з'єднання | ~30–64 КБ на з'єднання (буфери, HTTP-парсери, TLS-контекст) |
| **Запобіжники (Circuit Breaker)**| Лише за кількістю TCP-з'єднань | За кількістю запитів, чергою, 5xx та затримкою p99 |
| **Перевірка стану (Health)**| Базовий TCP handshake | Повноцінні HTTP/gRPC проби готовності |
| **Динамічне керування (xDS)**| LDS та CDS | Повний стек: LDS, RDS, CDS, EDS |
