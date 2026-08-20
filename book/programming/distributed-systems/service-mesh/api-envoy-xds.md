# 📋 Специфікація динамічного протоколу Envoy xDS v3 та декларативних маніфестів

Протокол xDS (англ. *XML/Extensible Discovery Service*, пізніше *universal Data Plane API*) є відкритим мережевим стандартом на базі gRPC та Protocol Buffers v3, розробленим для динамічного оновлення конфігурації проксі-серверів Envoy без перезапуску процесу. Площина управління (Control Plane) виступає gRPC-сервером, а сайдкар-проксі (Data Plane) підключаються як клієнти і в режимі реального часу отримують оновлення списків слухачів, маршрутів, кластерів та сертифікатів безпеки.

## Архітектура протоколу та життєвий цикл сесії

У традиційних проксі-серверах (Nginx, HAProxy) зміна конфігурації вимагала переписування конфігураційного файлу на диску та виконання сигналу перезавантаження процесу (`SIGHUP`). При високій частоті оновлень у динамічному кластері Kubernetes (сотні подій масштабування, перерозгортання та видалення подів на хвилину) перезапуск процесів призводить до вичерпання дескрипторів сокетів, сплесків затримок і втрати активних TCP-з'єднань.

Протокол xDS вирішує цю проблему за допомогою реактивної потокової доставки конфігураційних об'єктів. Проксі-сервер установлює постійне двонаправлене gRPC-з'єднання з площиною управління і підписується на ресурси певних типів. Усі структури даних у пам'яті Envoy захищені атомарними покажчиками (`std::shared_ptr` / Read-Copy-Update), що дозволяє миттєво підміняти таблиці маршрутизації та пули бекендів без блокування робочих потоків обробки мережевого трафіку.

### Транспортні моделі: State-of-the-World (SotW) проти Delta xDS

Протокол xDS підтримує дві взаємовиключні моделі обміну повідомленнями:

1. **State-of-the-World (SotW):** Повна передача стану. Щоразу, коли змінюється хоча б один кінцевий вузол або маршрут, Control Plane генерує і відправляє проксі повний масив усіх ресурсів цього типу. Ця модель проста в реалізації, але на масштабах понад тисячу сервісів створює гігантський надлишковий трафік серіалізації gRPC.
2. **Delta xDS (Incremental / Incremental ADS):** Інкрементальна доставка змін. Control Plane транслює клієнту виключно дельту: список новостворених або змінених ресурсів у полі `resources` та список видалених імен ресурсів у полі `removed_resources`. Це скорочує навантаження на мережу та процесор на 80–95%.

Для мінімізації кількості відкритих TCP-з'єднань використовується **Aggregated Discovery Service (ADS)** — єдиний мультиплексований gRPC-стрім (`/envoy.service.discovery.v3.AggregatedDiscoveryService/StreamAggregatedResources`), яким послідовно передаються всі типи ресурсів.

```protobuf
service AggregatedDiscoveryService {
  rpc StreamAggregatedResources(stream DiscoveryRequest) returns (stream DiscoveryResponse);
  rpc DeltaAggregatedResources(stream DeltaDiscoveryRequest) returns (stream DeltaDiscoveryResponse);
}
```

### Структура повідомлень та протокол підтвердження (ACK / NACK)

Обмін повідомленнями в xDS базується на строгому автоматі станів із підтвердженням кожної транзакції. Це запобігає ситуаціям, коли проксі переходить у неконсистентний стан через синтаксичну або логічну помилку в конфігурації.

```
Control Plane (Pilot)                             Envoy Sidecar (Data Plane)
       |                                                      |
       | <--- 1. DiscoveryRequest (type: CDS, version: "") -- |
       |                                                      |
       | --- 2. DiscoveryResponse (version: "v1", nonce: "A") -> (Валідація OK)
       |                                                      |
       | <--- 3. DiscoveryRequest (version: "v1", nonce: "A") - (ACK: успішно застосовано)
       |                                                      |
       | --- 4. DiscoveryResponse (version: "v2", nonce: "B") -> (Помилка валідації!)
       |                                                      |
       | <--- 5. DiscoveryRequest (version: "v1", nonce: "B", - (NACK: відхилено,
       |                          error_detail: "bad field")    збережено версію "v1")
```

#### Поля повідомлення запиту (`DiscoveryRequest`)

| Поле | Тип | Обов'язкове | Опис та семантика |
| :--- | :--- | :---: | :--- |
| `version_info` | `string` | Ні | Поточна версія конфігурації, успішно застосована клієнтом для даного `type_url`. Порожній рядок у першому запиті. |
| `node` | `Node` | Так (у першому запиті) | Структуровані метадані клієнта: унікальний ідентифікатор пода, ім'я кластера, версія бінарника, зона доступності та локальна IP-адреса. |
| `resource_names` | `repeated string` | Ні | Список конкретних імен ресурсів, на які підписується проксі (наприклад, ім'я маршруту `inbound_routes` для RDS). |
| `type_url` | `string` | Так | Уніфікований ідентифікатор типу запитуваного ресурсу (наприклад, `type.googleapis.com/envoy.config.cluster.v3.Cluster`). |
| `response_nonce` | `string` | Ні | Одноразовий маркер (`nonce`), отриманий у попередній відповіді `DiscoveryResponse`. Служить для захисту від гонок повідомлень. |
| `error_detail` | `google.rpc.Status` | Ні | Заповнюється **виключно при відхиленні (NACK)**. Містить цілочисельний код помилки та детальний текстовий опис причини збою валідації. |

#### Поля повідомлення відповіді (`DiscoveryResponse`)

| Поле | Тип | Опис та семантика |
| :--- | :--- | :--- |
| `version_info` | `string` | Новий глобальний ідентифікатор версії, згенерований сервером Control Plane для даного типу ресурсу. |
| `resources` | `repeated google.protobuf.Any` | Масив бінарно серіалізованих Protocol Buffers об'єктів відповідного типу `type_url`. |
| `type_url` | `string` | Тип ресурсів, що містяться в полі `resources`. |
| `nonce` | `string` | Унікальний криптографічний або числовий маркер відповіді, який клієнт зобов'язаний повернути у наступному запиті. |

## Головні типи ресурсів xDS v3 та їхня семантика

Конфігурація Envoy будується у вигляді строгої спрямованої ієрархії: **LDS → RDS → CDS → EDS**, де кожен наступний шар уточнює деталі виконання мережевого виклику.

### 1. LDS (Listener Discovery Service)

* **Type URL:** `type.googleapis.com/envoy.config.listener.v3.Listener`
* **Призначення:** Визначає мережеві інтерфейси та порти, які проксі відкриває для прослуховування вхідного трафіку, а також ланцюжки фільтрів L4/L7.

У типовій конфігурації сервісної сітки Envoy створює два головних слухача:
1. `virtualInbound` (порт 15006) — приймає весь перехоплений вхідний трафік пода, термінує mTLS і передає запити локальному застосунку.
2. `virtualOutbound` (порт 15001) — приймає весь вихідний трафік застосунку і спрямовує його у відповідні кластери зовнішніх сервісів.

Кожен слухач містить ланцюжок фільтрів мережевого рівня (`filter_chains`). Головним прикладним фільтром є `HttpConnectionManager` (HCM), який відповідає за розбір протоколів HTTP/1.1, HTTP/2 та gRPC, обробку заголовків, генерацію спанів трейсингу та передачу запиту внутрішньому роутеру.

```yaml
name: inbound_15006
address:
  socket_address:
    address: 0.0.0.0
    port_value: 15006
filter_chains:
  - filter_chain_match:
      transport_protocol: tls
      application_protocols: ["istio-peer-exchange", "istio", "http/1.1"]
    transport_socket:
      name: envoy.transport_sockets.tls
      typed_config:
        "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext
        common_tls_context:
          tls_certificate_sds_secret_configs:
            - name: default
              sds_config: { ads: {} }
    filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          stat_prefix: ingress_http
          rds:
            route_config_name: inbound_routes
            config_source: { ads: {} }
          http_filters:
            - name: envoy.filters.http.router
              typed_config:
                "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
```

### 2. RDS (Route Discovery Service)

* **Type URL:** `type.googleapis.com/envoy.config.route.v3.RouteConfiguration`
* **Призначення:** Описує таблиці динамічної маршрутизації L7 (HTTP/1.1, HTTP/2, gRPC).

RDS зіставляє вхідні HTTP-запити за доменами (`virtual_hosts`), шляхами (префікс, точний збіг або регулярний вираз) та заголовками. Маршрут визначає цільовий upstream-кластер, таймаут виклику, політику повторів (ретраїв) та правила канареечного розподілу ваг.

У конфігурації маршруту задаються такі ключові параметри:
* `timeout` — жорсткий глобальний таймаут на повне виконання операції (включаючи повтори).
* `retry_policy` — правила повторних спроб: `retry_on` (список кодів або подій збою), `num_retries` (максимальна кількість спроб), `per_try_timeout` (таймаут на одну спробу) та `retry_back_off` (експоненційний відступ із випадковим джитером для запобігання резонансним штормам).
* `weighted_clusters` — процентний розподіл трафіку між різними версіями бекенда для плавного викачування релізів.

```yaml
name: inbound_routes
virtual_hosts:
  - name: order_service_vhosts
    domains: ["*"]
    routes:
      - match:
          prefix: "/api/v1/orders"
          headers:
            - name: "x-env"
              exact_match: "canary"
        route:
          cluster: outbound|8080|canary|order.prod.svc.cluster.local
          timeout: 1.5s
          retry_policy:
            retry_on: "5xx,connect-failure,refused-stream"
            num_retries: 2
            per_try_timeout: 500ms
            retry_back_off:
              base_interval: 25ms
              max_interval: 250ms
      - match:
          prefix: "/api/v1/orders"
        route:
          weighted_clusters:
            clusters:
              - name: outbound|8080|v1|order.prod.svc.cluster.local
                weight: 90
              - name: outbound|8080|v2|order.prod.svc.cluster.local
                weight: 10
```

### 3. CDS (Cluster Discovery Service)

* **Type URL:** `type.googleapis.com/envoy.config.cluster.v3.Cluster`
* **Призначення:** Визначає логічну групу однорідних бекенд-серверів (Upstream Cluster), протокол взаємодії, алгоритм балансування та параметри стійкості.

CDS конфігурує:
* **Тип виявлення (`type`):** `EDS` (динамічний список із площини управління), `STATIC` (фіксовані IP), `STRICT_DNS` (періодичний резолв через DNS).
* **Алгоритм балансування (`lb_policy`):** `ROUND_ROBIN`, `LEAST_REQUEST`, `RING_HASH` (консистентне хешування), `MAGLEV`.
* **Запобіжники (`circuit_breakers`):** жорсткі пороги на максимальну кількість одночасних TCP-з'єднань (`max_connections`), чергу очікуючих HTTP-запитів (`max_pending_requests`), активних паралельних запитів (`max_requests`) і ретраїв (`max_retries`).
* **Виявлення викидів (`outlier_detection`):** правила автоматичної ізоляції нестабільних екземплярів при отриманні серії помилок 5xx (`consecutive_5xx`), базовий час блокування (`base_ejection_time`) і максимальний процент ізольованих хостів (`max_ejection_percent`).

```yaml
name: outbound|8080|v1|order.prod.svc.cluster.local
type: EDS
eds_cluster_config:
  eds_config: { ads: {} }
  service_name: outbound|8080|v1|order.prod.svc.cluster.local
lb_policy: LEAST_REQUEST
least_request_lb_config:
  choice_count: 2
connect_timeout: 0.25s
circuit_breakers:
  thresholds:
    - priority: DEFAULT
      max_connections: 1024
      max_pending_requests: 512
      max_requests: 2048
      max_retries: 3
outlier_detection:
  consecutive_5xx: 3
  interval: 10s
  base_ejection_time: 30s
  max_ejection_percent: 50
  enforcing_consecutive_5xx: 100
```

### 4. EDS (Endpoint Discovery Service)

* **Type URL:** `type.googleapis.com/envoy.config.endpoint.v3.ClusterLoadAssignment`
* **Призначення:** Доставляє фізичні адреси (IP та порт) конкретних контейнерів/подів, які обслуговують відповідний кластер.

EDS підтримує концепцію географічної близькості (**Locality-Weighted Load Balancing**). Ендпоінти групуються за регіонами (`region`), зонами доступності (`zone`) та пріоритетами (`priority`). Envoy автоматично направляє 100% запитів на поди всередині тієї самої зони доступності (Zone-Local), знижуючи мережеву затримку і фінансові витрати на міжзональний трафік у хмарі, і перемикається на сусідні зони лише при деградації локальних подів.

Кожен ендпоінт містить статус здоров'я (`health_status`):
* `HEALTHY` — вузол доступний для маршрутизації.
* `UNHEALTHY` — вузол не пройшов перевірку життєздатності (Health Check).
* `DRAINING` — вузол готується до завершення роботи (Graceful Shutdown): нові з'єднання не надсилаються, але поточні активні запити дообслуговуються.

```yaml
cluster_name: outbound|8080|v1|order.prod.svc.cluster.local
endpoints:
  - locality:
      region: eu-central-1
      zone: eu-central-1a
    priority: 0
    lb_endpoints:
      - endpoint:
          address:
            socket_address:
              address: 10.244.1.45
              port_value: 8080
        health_status: HEALTHY
        load_balancing_weight: 100
      - endpoint:
          address:
            socket_address:
              address: 10.244.2.89
              port_value: 8080
        health_status: HEALTHY
        load_balancing_weight: 100
```

### 5. SDS (Secret Discovery Service)

* **Type URL:** `type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.Secret`
* **Призначення:** Динамічна доставка та безпечна безшовна ротація приватних ключів і X.509-сертифікатів робочих навантажень (SPIFFE SVID).

SDS усуває необхідність монтувати сертифікати у вигляді статичних файлів із дисків Secret Kubernetes. Коли сертифікат наближається до завершення терміну дії, локальний агент безпеки (`istio-agent`) генерує новий закритий ключ у пам'яті, отримує підписаний сертифікат від Control Plane CA і передає його Envoy через внутрішній UNIX Domain Socket. Envoy підміняє активний TLS-контекст на льоту без переривання існуючих TLS-сесій.

Контекст перевірки (`validation_context`) налаштовує список довірених кореневих сертифікатів (`trusted_ca`) та точні патерни зіставлення `match_typed_subject_alt_names` для перевірки SPIFFE ID віддаленого клієнта чи сервера.

```yaml
name: default
tls_certificate:
  certificate_chain:
    inline_bytes: "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0t..."
  private_key:
    inline_bytes: "LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLS..."
validation_context:
  trusted_ca:
    inline_bytes: "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0t..."
  match_typed_subject_alt_names:
    - matcher:
        exact: "spiffe://cluster.local/ns/prod/sa/order-service-account"
      san_type: URI
```

## Зіставлення декларативних маніфестів Kubernetes (Istio CRD) із ресурсами xDS

Інженери керують сервісною сіткою за допомогою декларативних маніфестів Kubernetes Custom Resource Definitions (CRD). Площина управління виконує роль компілятора: вона відстежує зміни CRD через Kubernetes API Watch, перетворює їх на графі об'єктів xDS і транслює сайдкарам.

### Трансляція Istio VirtualService → Envoy RDS

Маніфест `VirtualService` дозволяє налаштовувати маршрутизацію, поділ трафіку, таймаути та ретраї. Під капотом Control Plane перетворює його на секцію `virtual_hosts.routes` у ресурсі RDS.

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: order-route
  namespace: prod
spec:
  hosts:
    - order-service.prod.svc.cluster.local
  http:
    - match:
        - headers:
            canary-user:
              exact: "true"
      route:
        - destination:
            host: order-service.prod.svc.cluster.local
            subset: canary
    - route:
        - destination:
            host: order-service.prod.svc.cluster.local
            subset: v1
          weight: 90
        - destination:
            host: order-service.prod.svc.cluster.local
            subset: v2
          weight: 10
      timeout: 2s
      retries:
        attempts: 3
        perTryTimeout: 500ms
        retryOn: "5xx,connect-failure"
```

### Трансляція Istio DestinationRule → Envoy CDS

Маніфест `DestinationRule` налаштовує політики, які застосовуються до трафіку після завершення маршрутизації: алгоритми балансування, режими взаємного TLS, налаштування пулів з'єднань і пороги виявлення викидів (Outlier Detection). Control Plane компілює цей маніфест у параметри відповідного об'єкта `Cluster` в CDS.

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: order-destination
  namespace: prod
spec:
  host: order-service.prod.svc.cluster.local
  trafficPolicy:
    loadBalancer:
      simple: LEAST_REQUEST
    connectionPool:
      tcp:
        maxConnections: 1024
      http:
        http1MaxPendingRequests: 100
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutive5xxErrors: 3
      interval: 10s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
    tls:
      mode: ISTIO_MUTUAL
  subsets:
    - name: v1
      labels:
        version: v1
    - name: v2
      labels:
        version: v2
    - name: canary
      labels:
        version: canary
```

## Діагностика та інспекція стану xDS через Envoy Admin API

Кожен сайдкар Envoy відкриває внутрішній адміністративний інтерфейс (за замовчуванням `127.0.0.1:15000`), що дозволяє інженерам діагностувати поточний стан площини даних:

* `GET /config_dump` — виводить повний JSON-знімок усіх активних ресурсів LDS, RDS, CDS, EDS та SDS, застосованих у пам'яті проксі. Дозволяє миттєво виявити розбіжність версій або стан NACK.
* `GET /clusters` — відображає поточний стан усіх upstream-бекендів: кількість активних з'єднань, стан працездатності (healthy/ejected) та лічильники помилок 5xx для кожного конкретного IP.
* `GET /stats/prometheus` — генерує повний масив внутрішніх метрик у форматі Prometheus (лічильники ретраїв, скинутих з'єднань, затримок рукостискань TLS).
* `POST /logging?level=debug` — динамічно перемикає рівень логування окремих підсистем (наприклад, `connection`, `router`, `http`) без перезапуску сайдкара.
