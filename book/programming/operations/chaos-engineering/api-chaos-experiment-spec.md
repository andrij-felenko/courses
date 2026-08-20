# 📋 Декларативна специфікація та контракт хаос-експериментів

Цей довідник визначає формальну декларативну специфікацію, схеми даних та системні контракти для опису, оркестрації та автоматизованого виконання хаос-експериментів у хмарних і розподілених середовищах.

## Загальна структура специфікації (Chaos Experiment Schema)

Декларативний контракт хаос-експерименту стандартизує п'ять обов'язкових блоків:
1. **Метадані та область дії (Metadata & Target Selector):** Визначення цільових вузлів, просторів імен (namespaces), контейнерів або мікросервісів із заданням відсотка або абсолютної кількості мішеней.
2. **Проби стійкого стану (Steady State Probes):** Критерії перевірки індикаторів здоров'я (SLI) до, під час та після ін'єкції збою.
3. **Дія ін'єкції несправності (Fault Action):** Конкретний тип і параметри збою (мережа, процеси, ресурси CPU/пам'яті, прикладні HTTP/gRPC виклики, час або DNS).
4. **Контроль радіуса ураження та дедлайнів (Blast Radius & Guardrails):** Обмеження тривалості, частоти повторів, лімітів навантаження та умов спрацьвування аварійного вимикача (Kill Switch).
5. **Протокол відкату та компенсації (Rollback & Cleanup Protocol):** Автоматичні команди та процедури очищення середовища після завершення або аварійної зупинки тесту.

Нижче наведено повну декларативну схему у форматі маніфесту Kubernetes Custom Resource Definition (CRD), сумісну зі стандартами OpenChaos та Cloud Native Chaos Frameworks:

```yaml
apiVersion: chaos.engineering/v1alpha1
kind: ChaosExperiment
metadata:
  name: checkout-payment-latency-resilience
  namespace: e-commerce-prod
  labels:
    tier: business-critical
    app.kubernetes.io/part-of: checkout-flow
spec:
  # 1. Область дії та вибір мішеней (Target Selector)
  selector:
    namespaces:
      - e-commerce-prod
    labelSelectors:
      app: checkout-service
      role: backend
    cohort:
      mode: FixedPercent
      value: 10 # Вносити збій лише у 10% екземплярів (Canary Cohort)
    trafficFilter:
      headers:
        x-chaos-context: "experiment-eval"
      syntheticOnly: false

  # 2. Перевірки стійкого стану (Steady State Probes)
  steadyStateProbes:
    - name: checkout-success-rate-promql
      type: Prometheus
      interval: 5s
      timeout: 2s
      tolerance:
        operator: GreaterThanOrEqual
        thresholdValue: 99.9 # SLO: успішність замовлень >= 99.9%
      prometheus:
        endpoint: "http://prometheus-k8s.monitoring.svc:9090"
        query: >-
          sum(rate(checkout_orders_total{status="success"}[1m])) 
          / sum(rate(checkout_orders_total[1m])) * 100

    - name: payment-gateway-p99-latency
      type: Prometheus
      interval: 5s
      timeout: 2s
      tolerance:
        operator: LessThanOrEqual
        thresholdValue: 350.0 # Latency p99 <= 350 мс
      prometheus:
        endpoint: "http://prometheus-k8s.monitoring.svc:9090"
        query: >-
          histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{service="checkout"}[1m])) by (le)) * 1000

    - name: healthz-http-probe
      type: HTTPGet
      interval: 3s
      timeout: 1s
      tolerance:
        operator: Equal
        expectedStatusCode: 200
      httpGet:
        path: /healthz/ready
        port: 8080

  # 3. Дія ін'єкції збою (Fault Action)
  action: NetworkChaos
  networkChaos:
    targetDirection: Egress
    targetCIDR:
      - "10.96.120.0/24" # Мережа підсистеми платіжного шлюзу (Payment Gateway)
    targetPort: 8443
    faultType: LatencyAndJitter
    latency:
      delay: "250ms"
      jitter: "30ms"
      distribution: "normal" # normal | uniform | pareto
      correlation: "25%"
    packetLoss:
      percentage: 2.5 # 2.5% випадкової втрати TCP-пакетів

  # 4. Радіус ураження та дедлайни (Blast Radius & Guardrails)
  guardrails:
    duration: "180s" # Максимальна тривалість активної фази
    watchdogTTL: "200s" # Аварійний таймер автономного скидання правил
    emergencyAbortTriggers:
      - metric: checkout-success-rate-promql
        condition: "value < 99.5" # Негайний Abort, якщо успішність впаде нижче 99.5%
      - metric: error-budget-burn-rate
        condition: "burnRate > 14.4" # 1-годинний ліміт споживання бюджету помилок
    schedule:
      allowedTimeWindows:
        - days: ["Monday", "Tuesday", "Wednesday", "Thursday"]
          startTime: "10:00"
          endTime: "16:00"
          timezone: "Europe/Kyiv"

  # 5. Протокол відкату та сповіщення (Rollback Protocol)
  rollback:
    mode: Immediate
    remediationAction: RestoreNetworkQdisc
    onFailureHooks:
      - type: Webhook
        url: "https://alertmanager.internal/api/v2/alerts"
        payload:
          severity: "critical"
          summary: "Хаос-експеримент аварійно зупинено через порушення SLO!"
```

## 1. Специфікація селектора мішеней (Target Selector)

Селектор мішеней визначає точну множину вузлів, контейнерів або процесів, на які поширюється дія ін'єктора. Головний інженерний принцип селектора — детермінованість та ізоляція. Якщо селектор складено некоректно, ін'єкція збою може випадково торкнутися критичних системних компонентів кластера (наприклад, etcd або CoreDNS).

### Таблиця полів вибору мішеней (`spec.selector`)

| Поле | Тип | Обов'язкове | Опис та обмеження |
| :--- | :--- | :--- | :--- |
| `namespaces` | `[]string` | Так | Список просторів імен Kubernetes, у межах яких проводиться експеримент. |
| `labelSelectors` | `map[string]string` | Так | Набір міток (Labels) для пошуку цільових Pod усередині простору імен. |
| `annotationSelectors`| `map[string]string` | Ні | Фільтрація Pod за анотаціями (наприклад, `chaos.engineering/enabled: "true"`). |
| `fieldSelectors` | `map[string]string` | Ні | Фільтрація за системними полями Kubernetes (наприклад, `status.phase=Running`). |
| `nodes` | `[]string` | Ні | Обмеження списку фізичних або віртуальних нод кластера. |
| `nodeSelectors` | `map[string]string` | Ні | Селектор міток нод (наприклад, `topology.kubernetes.io/zone=eu-central-1a`). |
| `containers` | `[]string` | Ні | Список імен конкретних контейнерів усередині цільового Pod. Якщо не вказано — застосовується до всіх контейнерів. |
| `cohort.mode` | `string` | Так | Режим вибірки мішеней: `FixedPercent`, `FixedCount`, `All`, `OneRandom`. |
| `cohort.value` | `int` | Так | Відсоток (1–100) або точна кількість інстансів, що підлягають ін'єкції. |
| `trafficFilter.headers` | `map[string]string` | Ні | Набір HTTP-заголовків або Baggage OpenTelemetry для фільтрації трафіку. |
| `trafficFilter.syntheticOnly` | `bool` | Ні | Якщо `true`, збій активується лише для синтетичного тестового трафіку. За замовчуванням: `false`. |

### Семантика режимів когорт (Cohort Selection Semantics)
- `FixedPercent`: Оператор хаосу обчислює кількість цільових інстансів як `ceil(total_pods * value / 100)`. Якщо в кластері розгорнуто 20 Pod і задано значення `10%`, збій буде внесено рівно у 2 Pod. При масштабуванні кластера (Horizontal Pod Autoscaling) кількість інфікованих Pod автоматично перераховується контролером.
- `FixedCount`: Жорстко фіксована кількість Pod (наприклад, рівно 1 Pod). Якщо кількість живих Pod опускається нижче значення `value`, контролер переводить експеримент у стан очікування або генерує попередження `WarningTargetUnderflow`.
- `OneRandom`: Випадковий вибір рівно одного екземпляра з множини доступних на кожній ітерації таймера.

## 2. Специфікація проб стійкого стану (Steady State Probes)

Проби стійкого стану є головним механізмом наукового методу в хаос-інженерії. Проби виконуються за трьома фазовими розкладами:
1. **Пре-валідація (Pre-Check):** Перевірка здоров'я системи перед внесенням будь-яких збоїв. Якщо система вже перебуває в деградованому стані (SLO вже порушено), експеримент навіть не починається.
2. **Безперервний моніторинг (In-Flight Evaluation):** Періодичне опитування метрик під час активної ін'єкції збою.
3. **Пост-валідація (Post-Check):** Перевірка повного повернення метрик до базового стану після завершення відкату правил.

### Таблиця параметрів проб (`spec.steadyStateProbes[]`)

| Поле | Тип | Допустимі значення | Опис |
| :--- | :--- | :--- | :--- |
| `name` | `string` | Унікальний рядок | Ідентифікатор проби для телеметрії та звітів. |
| `type` | `string` | `Prometheus`, `HTTPGet`, `Command`, `K8sResource`, `gRPCHealth` | Механізм виконання перевірки стійкого стану. |
| `interval` | `duration` | Наприклад `2s`, `5s`, `10s` | Періодичність опитування індикатора SLI. |
| `timeout` | `duration` | Наприклад `500ms`, `2s` | Максимальний час очікування відповіді від системи моніторингу. |
| `failureThreshold` | `int` | За замовчуванням `1` | Кількість послідовних збоїв проби, необхідна для активації екстреного аварійного відкату (Kill Switch). |
| `tolerance.operator` | `string` | `Equal`, `NotEqual`, `LessThan`, `LessThanOrEqual`, `GreaterThan`, `GreaterThanOrEqual`, `Range` | Оператор порівняння метрики з еталонним значенням. |
| `tolerance.thresholdValue` | `float64` | Будь-яке дійсне число | Числовий поріг безпеки (наприклад, RPS або затримка). |

### Специфікація типів проб та алгоритми оцінки

1. **Prometheus / PromQL Проба:**
   Опитує HTTP API Prometheus (`/api/v1/query`). Контролер парсить JSON-відповідь і витягує числовий результат із поля `data.result[0].value[1]`.
   - Якщо PromQL-запит повертає порожній масив векторів (`result: []`), це свідчить про зникнення метрики, що автоматично трактується як збій проби (`ErrProbeEmptyMetric`).
   - Для розрахунку швидкості спалювання бюджету помилок (Error Budget Burn Rate) використовується стандартна формула Google SRE: відношення поточної частоти помилок за 1-хвилинне вікно до допустимої річної частки відмов, помножене на часовий коефіцієнт.

2. **HTTPGet Проба:**
   Виконує синхронний HTTP-запит до вказаного URL через клієнт із жорстко обмеженим пулом з'єднань:
   - `path` (`string`): Шлях ендпоінта перевірки здоров'я (наприклад, `/healthz/ready`).
   - `port` (`int`): TCP-порт контейнера.
   - `headers` (`map[string]string`): Заголовки запиту (наприклад, `Authorization: Bearer ...`).
   - `expectedStatusCode` (`int`): Очікуваний код відповіді сервера (типово `200`). Якщо сервер повертає статус `503 Service Unavailable`, проба фіксує неготовність вузла до прийому навантаження.

3. **gRPC Health Checking Проба:**
   Виконує виклик стандартного gRPC Health Checking Protocol (`grpc.health.v1.Health/Check`):
   - `service` (`string`): Назва сервісу (пусто для загального статусу сервера).
   - `expectedStatus` (`string`): Очікуваний статус: `SERVING` (успіх), `NOT_SERVING`, `UNKNOWN`. Будь-яка транспортна помилка з'єднання (`UNAVAILABLE`) фіксує відмову вузла.

4. **Command Проба:**
   Виконує бінарний файл або скрипт у просторі користувача цільового контейнера через системний виклик `exec`:
   - `command` (`[]string`): Список аргументів команди (наприклад `["/usr/bin/curl", "-f", "http://localhost:8080/metrics"]`). Очікується повернення коду виходу `0`. Якщо процес завершується з ненульовим кодом або зазнає тайм-ауту, проба вважається проваленою.

## 3. Матриця дій ін'єкції збоїв (Fault Action Matrix)

Контракт ін'єкції несправностей розділений на шість функціональних доменів: мережа, обчислювальні ресурси, контейнери/процеси, прикладні HTTP-протоколи, системний час та DNS.

```
┌────────────────────────────────────────────────────────────────────────┐
│                      Дії ін'єкції збоїв (Actions)                      │
├───────────────────┬───────────────────┬────────────────────────────────┤
│ Категорія         │ Тип дії           │ Механізм виконання в системі   │
├───────────────────┼───────────────────┼────────────────────────────────┤
│ Мережа            │ NetworkChaos      │ Linux Traffic Control (netem)  │
│ Обчислення        │ StressChaos       │ cgroups v2 + stress-ng         │
│ Контейнери/Процеси│ PodChaos          │ SIGKILL / SIGSTOP / cgroups    │
│ Прикладний рівень │ HTTPChaos         │ Envoy / Service Mesh / Proxy   │
│ Системний час     │ TimeChaos         │ VDSO clock spoofing (ptrace)   │
│ DNS               │ DNSChaos          │ CoreDNS interceptor / iptables │
└───────────────────┴───────────────────┴────────────────────────────────┘
```

### 1. `NetworkChaos` — Специфікація мережевих несправностей

Мережеві несправності реалізуються через підсистему ядра Linux Traffic Control (`tc-netem`) та пакетні фільтри `iptables`/`nftables`.

```yaml
networkChaos:
  targetDirection: Egress # Ingress | Egress | Both
  targetCIDR:
    - "10.244.0.0/16"
  targetPort: 5432
  protocol: TCP # TCP | UDP | ICMP
  faultType: LatencyAndJitter # Latency | Loss | Duplicate | Corrupt | Bandwidth
  latency:
    delay: "150ms"
    jitter: "20ms"
    distribution: "normal" # uniform | normal | pareto | paretonormal
    correlation: "25%"
  packetLoss:
    percentage: 5.0
    correlation: "10%"
  bandwidth:
    rate: "10mbps"
    limit: 20000 # Розмір черги буфера в байтах
    buffer: 1600 # Розмір пакета в байтах
```

#### Поля конфігурації NetworkChaos:
- **`targetDirection`:** Задає напрямок ін'єкції. `Egress` вносить затримку у вихідні пакети (найбільш реалістично для емуляції уповільнення зовнішніх API), `Ingress` — у вхідні пакети через інтерфейс IFB (Intermediate Functional Block).
- **`latency.correlation`:** Відсоток статистичної залежності між затримкою поточного пакета та затримкою попереднього. Запобігає неприродно різким стрибкам затримки між сусідніми пакетами одного TCP-потоку.
- **`packetLoss.correlation`:** Коефіцієнт кореляції Бернуллі. Висока кореляція моделює серійну втрату пакетів (Burst Packet Loss), характерну для переповнення буферів апаратних комутаторів.

### 2. `StressChaos` — Специфікація виснаження ресурсів

Реалізується через створення дочірніх процесів генерації синтетичного навантаження всередині контрольної групи cgroups v2 цільового контейнера.

```yaml
stressChaos:
  cpu:
    workers: 4
    loadPercent: 80 # Навантаження 80% кожного виділеного ядра
    options: ["--cpu-method", "matrixprod"]
  memory:
    workers: 2
    size: "1024MB"
    oomScoreAdj: 500 # Підвищення пріоритету OOM Killer для тестового воркера
  io:
    workers: 2
    bytes: "512MB"
    options: ["--hdd-sync"]
```

#### Поля конфігурації StressChaos:
- **`cpu.loadPercent`:** Контролює частку квантів часу планувальника CFS, які споживає процес навантаження, залишаючи залишок потужності для основного застосунку.
- **`memory.size`:** Обсяг алокації сторінок пам'яті через виклики `mmap()` та `memset()`. Якщо застосунок не має обмежень у `cgroup`, це викликає запуск витіснення сторінок у swap або активацію `kswapd`.

### 3. `PodChaos` — Збої життєвого циклу контейнерів

Керує станами контейнерів та процесів усередині просторів імен Linux.

```yaml
podChaos:
  action: PodFailure # PodKill | PodFailure | ContainerKill
  gracePeriod: 0 # 0 = негайний SIGKILL, >0 = штатне вимкнення SIGTERM
  containerNames:
    - payment-app
```

#### Семантика дій PodChaos:
- **`PodKill`:** Оркестратор надсилає сигнал зупинки Pod через API Kubernetes, ініціюючи видалення та перестворення Pod на сусідньому вузлі.
- **`PodFailure`:** Мутуючий вебхук перехоплює конфігурацію Pod і підміняє базовий образ на заблокований образ-пастку (Pause Container), унеможливлюючи обробку трафіку, але утримуючи IP-адресу в кластері. Це дозволяє протестувати реакцію балансувальників на живий IP із мертвим сервісом.
- **`ContainerKill`:** Демон надсилає прямий сигнал `SIGKILL` головному процесу (PID 1) контейнера всередині його простору імен безпосередньо через runtime containerd/CRI.

### 4. `HTTPChaos` — Ін'єкція на рівні HTTP/gRPC викликів

Працює через перехоплення трафіку Sidecar-проксі Envoy або eBPF сокетних фільтрів.

```yaml
httpChaos:
  targetService: "recommendation-service"
  port: 8080
  match:
    path: "^/api/v2/recommendations/.*$"
    method: "GET"
    headers:
      x-user-tier: "standard"
  fault:
    abort:
      httpStatus: 503
      percentage: 25.0 # 25% запитів повертають 503
    delay:
      duration: "1200ms"
      percentage: 50.0 # 50% запитів затримуються на 1.2 с
    replace:
      body: '{"status":"fallback","items":[]}' # Підміна тіла відповіді
```

### 5. `DNSChaos` — Збої системи резолвінгу доменних імен

Ін'єктор перехоплює UDP/TCP трафік до порту 53 всередині простору імен мережі контейнера.

```yaml
dnsChaos:
  action: Error # Error | Random | Delay
  domainPattern: ".*\\.internal\\.corp$"
  errorCode: NXDOMAIN # SERVFAIL | NXDOMAIN | REFUSED
  delay: "2000ms"
```

### 6. `JVMChaos` — Ін'єкція збоїв на рівні віртуальної машини Java

Для застосунків, що виконуються всередині JVM (Java, Kotlin, Scala), хаос-ін'єкція реалізується за допомогою динамічного підключення Java-агента через інтерфейс JVMTI (JVM Tool Interface) або фреймворк Byteman:
- Ін'єкція винятків: Агент модифікує байт-код методу на льоту, змушуючи його генерувати виняток `java.io.IOException` або `java.sql.SQLException` при вході у метод.
- Затримка виконання методу: Вставка інструкції `Thread.sleep()` безпосередньо у тіло методу бізнес-логіки.
- Примусове повернення підміненого значення: Метод повертає порожній об'єкт `null` або дефолтний DTO, перевіряючи коректність роботи захисних конструкцій застосунку.

## 4. Контроль радіуса ураження та дедлайни (Guardrails & Deadlines)

Секція `spec.guardrails` визначає жорсткі межі безпеки, які автоматично зупиняють експеримент за найменшої загрози стабільності продуктивного середовища.

### Таблиця параметрів безпеки (`spec.guardrails`)

| Поле | Тип | Опис та обмеження |
| :--- | :--- | :--- |
| `duration` | `duration` | Загальний час активної фази ін'єкції (наприклад `300s`, `10m`). |
| `watchdogTTL` | `duration` | Автономний час життя правил ядра (TTL). Запобігає зависанню правил при падінні оператора. |
| `emergencyAbortTriggers` | `[]AbortTrigger` | Список критичних умов, за яких експеримент негайно зупиняється (SLO Breach, Panic Rate). |
| `maxConcurrentTargets`| `int` | Максимальна кількість Pod, які можуть перебувати під дією хаосу одночасно в усьому кластері. |
| `schedule.allowedTimeWindows` | `[]TimeWindow` | Дозволені часові вікна для запуску хаосу (заборона запусків у вихідні або вночі). |

### Специфікація тригерів аварійного вимкнення (Emergency Abort Triggers)
Кожен тригер визначає метрику та умову порівняння:
```yaml
emergencyAbortTriggers:
  - metric: checkout-error-rate
    condition: "value > 1.0" # Якщо загальний рівень помилок перевищує 1.0%
  - metric: error-budget-burn-rate
    condition: "burnRate > 14.4" # Споживання понад 2% місячного бюджету помилок за годину
  - metric: database-connection-pool-exhaustion
    condition: "idleConnections < 2"
```

Якщо під час активної ін'єкції контролер фіксує виконання будь-якої з цих умов:
1. Контролер миттєво генерує команду `EmergencyRollback`.
2. Правила ядра Linux TC, cgroups або Envoy фільтри демонтуються за час, що не перевищує 500 мілісекунд.
3. Експеримент переходить у статус `Aborted` з фіксацією детальної телеметрії порушення.

## 5. Безпека, RBAC та ізоляція привілеїв у кластері

Виконання хаос-експериментів у продуктивному середовищі вимагає суворого розмежування прав доступу та контролю привілеїв ядра:

1. **Модель розділення обов'язків (RBAC Separation):**
   - **Chaos Controller (Керуюча площина):** Працює під стандартним ServiceAccount без підвищених привілеїв ОС. Має права на читання та модифікацію лише CRD-об'єктів хаосу та Pod у цільових просторах імен.
   - **Chaos Daemon (DaemonSet на кожній ноді):** Виконує низькорівневі маніпуляції з ядром хоста. Потребує набору Linux Capabilities:
     - `CAP_NET_ADMIN`: Необхідний для створення сокетів Netlink та налаштування дисциплін черги `tc-netem` у просторах імен мережі контейнерів (`/proc/$PID/ns/net`).
     - `CAP_SYS_PTRACE`: Необхідний для перехоплення системних викликів за допомогою `ptrace` під час ін'єкції затримок часу (TimeChaos) або симуляції дискових помилок.
     - `CAP_SYS_ADMIN`: Використовується для завантаження eBPF-програм та маніпуляції контрольними групами `/sys/fs/cgroup`.
2. **Захист критичних системних просторів імен (Namespace Whitelisting & Denylisting):**
   Контролер має вбудовану валідаційну політику (Admission Webhook), яка безумовно блокує застосування будь-яких хаос-маніфестів, спрямованих на системні простори імен `kube-system`, `monitoring`, `vault` або `ingress-nginx`. Спроба націлити `PodKill` або `NetworkChaos` на системний DNS або брокер секретів повертає помилку `ErrNamespaceForbidden`.

## 6. Контекстне маркування трафіку та W3C Baggage

Для забезпечення хірургічної точності ін'єкцій у мікросервісних ланцюжках специфікація підтримує стандарт контекстного поширення W3C Trace Context та Baggage:

```http
GET /api/v1/orders HTTP/1.1
Host: order-service.internal
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
baggage: chaos-experiment-id=exp-chk-42,chaos-fault=latency-300ms,chaos-canary=true
```

Коли запит проходить крізь ланцюжок із п'яти мікросервісів, клієнтські RPC-бібліотеки та Envoy-sidecar автоматично прокидають заголовок `baggage`. Ін'єктор активує затримку або повертає помилку лише тоді, коли вхідний запит містить відповідний контекстний маркер. Це дозволяє безпечно направляти синтетичний тестовий трафік крізь усю продуктивну інфраструктуру, не впливаючи на жодного реального користувача.

## 7. Журналювання подій Kubernetes та аудит-трейл

Кожна зміна стану експерименту транслюється у стандартний потік подій Kubernetes Events (`kubectl get events`):
- `Type: Normal, Reason: ChaosInjected`: Зафіксовано успішне накладання мережевих або ресурсних обмежень на вказані цільові Pod.
- `Type: Warning, Reason: ProbeThresholdBreached`: Значення індикатора SLI наблизилося до критичної межі допуску.
- `Type: Warning, Reason: EmergencyAbortTriggered`: Автоматичний вимикач зупинив тест через порушення порогу стійкого стану.
- `Type: Normal, Reason: ChaosCleaned`: Усі правила ядра демонтовано, середовище повернуто до базового стану.

Ці події фіксуються в системному Audit Log кластера для подальшого розбору інцидентів та верифікації відповідності політикам безпеки (Compliance).

## 8. Протокол відновлення та очищення середовища (Cleanup Protocol)

Під час завершення експерименту (штатного або аварійного) контролер хаосу зобов'язаний виконати детерміновану послідовність операцій відновлення:

1. **Демонтаж правил Linux Traffic Control:** Контролер відкриває Netlink-сокет до мережевого простору імен цільового Pod і надсилає повідомлення `RTM_DELQDISC` для видалення всіх правил `netem`. Інтерфейс повертається до стандартної конфігурації без переривання активних TCP-сесій.
2. **Скидання лімітів cgroups v2:** Якщо під час тесту накладалися обмеження на CPU або пам'ять, у файли `cpu.max` та `memory.high` записується значення `max`, повертаючи процесу повну обчислювальну потужність.
3. **Очищення eBPF-мап:** Програми перехоплення системних викликів видаляють фільтраційні записи з мап `BPF_MAP_TYPE_HASH`, припиняючи модифікацію результатів викликів `connect()` та `read()`.
4. **Видалення Sidecar-фільтрів Envoy:** Надсилається адміністративна команда оновлення конфігурації через LDS (Listener Discovery Service), яка вилучає фільтри `envoy.filters.http.fault` із конвеєра обробки запитів.
5. **Верифікація чистоти стану (State Cleanliness Assertion):** Контролер виконує додатковий цикл проб. Якщо мережевий джитер або рівень штучних помилок не повертається до нуля протягом 5 секунд, генерується критичний алерт `ErrRollbackVerificationFailed` для чергової зміни SRE.

## 9. Стан виконання та телеметрія (`status`)

Об'єкт `status` ведеться оператором хаосу в режимі реального часу для повної прозорості спостережуваності:

```yaml
status:
  phase: Running # Pending | Injected | Running | Aborting | Completed | Failed | Aborted
  startTime: "2026-08-20T10:15:00Z"
  endTime: null
  activeDuration: "1m42s"
  injectedTargets:
    - podName: checkout-service-7bb48c68f9-4z8kl
      nodeName: k8s-worker-pool-04
      ip: "10.244.3.42"
      targetInterface: "eth0"
      qdiscHandle: "1:0"
      status: Active
    - podName: checkout-service-7bb48c68f9-9q2xm
      nodeName: k8s-worker-pool-07
      ip: "10.244.5.18"
      targetInterface: "eth0"
      qdiscHandle: "1:0"
      status: Active
  probeResults:
    - name: checkout-success-rate-promql
      lastChecked: "2026-08-20T10:16:30Z"
      lastObservedValue: 99.94
      status: Healthy
      violationsCount: 0
    - name: payment-gateway-p99-latency
      lastChecked: "2026-08-20T10:16:30Z"
      lastObservedValue: 284.5
      status: Healthy
      violationsCount: 0
  experimentSummary:
    totalProbesEvaluated: 36
    sloViolationsCount: 0
    rollbackExecuted: false
    finalVerdict: Undetermined # HypothesisConfirmed | HypothesisRejected | Inconclusive
```

## 10. Скінченний автомат фаз виконання (Execution Phases)

Життєвий цикл хаос-ресурсу в кластері підпорядковується суворому скінченному автомату станів:

```
[Pending] ──(Валідація селекторів та базового SLI)──> [Injected]
   │                                                       │
   ▼ (Помилка селектора / недоступний Prometheus)          ▼ (Активація правил)
[Failed]                                              [Running]
                                                           │
          ┌────────────────────────────────────────────────┴───────────────────────┐
          ▼ (Вичерпано duration / успіх)                                           ▼ (Порушення проби SLI / Watchdog)
    [Completed]                                                               [Aborting]
          │                                                                        │
          ▼ (Зняття правил qdisc / cgroups)                                        ▼ (Екстрений Rollback + сповіщення)
    [Cleaned]                                                                 [Aborted]
```

### Коди помилок та причини завершення (`status.conditions[].reason`)

| Код аварії (`Reason`) | Опис причини |
| :--- | :--- |
| `ErrProbeSLOBreach` | Значення проби стійкого стану вийшло за межі допуску `tolerance`. |
| `ErrWatchdogTimeout` | Сплив дедлайн `watchdogTTL` до отримання сигналу штатного завершення. |
| `ErrTargetLost` | Усі цільові Pod зникли або зазнали падіння вузла хоста. |
| `ErrPrometheusUnreachable`| Моніторинг не зміг отримати значення SLI за час `timeout`. |
| `ErrRollbackFailed` | Системний виклик видалення правил ядра повернув помилку (потрібне втручання SRE-інженера). |
| `ErrPreCheckFailed` | Базовий стан системи перед початком експерименту не відповідав критеріям здоров'я. |
| `ErrScheduleDisallowed` | Запуск заблоковано через вихід за межі дозволеного часового вікна. |

## 11. Протокол генерації фінального звіту та верифікації гіпотези

Після завершення фази очищення оператор хаосу автоматично формує об'єкт висновку `finalVerdict`:

1. **`HypothesisConfirmed` (Гіпотезу підтверджено):**
   - Усі проби стійкого стану залишалися в межах норми протягом 100% часу ін'єкції.
   - Механізми відмовостійкості (Circuit Breaker, локальні кеші, повтори з відступом) спрацювали коректно.
   - Деградація продуктивності не перевищила встановлені межі SLO.

2. **`HypothesisRejected` (Гіпотезу спростовано):**
   - Експеримент виявив приховану системну вразливість (наприклад, каскадне падіння бази даних при затримці мікросервісу).
   - Спрацював тригер аварійного вимкнення (`ErrProbeSLOBreach`).
   - Оператор автоматично створює інцидент у системі відстеження помилок (Jira / GitHub Issues) із детальним дампом метрик та розподілених трейсів.

3. **`Inconclusive` (Результат невизначений):**
   - Під час експерименту цільовий сервіс не отримав достатнього обсягу вхідного трафіку для статистично достовірного висновку (наприклад, менше 100 запитів).
   - Експеримент потребує повторного проведення під піковим навантаженням або з генерацією синтетичного трафіку.
