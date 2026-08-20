# 📋 Декларативні специфікації прогресивної доставки: Argo Rollouts, Flagger та Envoy Route Configuration

У сучасних хмарних інфраструктурах на базі Kubernetes та сервісних сіток (Service Mesh) керування канарковим розгортанням виконується за допомогою декларативних специфікацій. Замість імперативних скриптів інженери описують бажаний стан релізу у формі користувацьких ресурсів (англ. *Custom Resource Definitions*, CRD) та конфігурацій маршрутизації L7-проксі.

Декларативний підхід забезпечує відтворюваність інфраструктури: стан конвеєра, критерії аналізу метрик, правила аварійного відкату та розклад зважування трафіку зберігаються в системі контролю версій Git (методологія GitOps). Контролери прогресивної доставки безперервно звіряють поточний стан кластера з оголошеним у маніфесті, самостійно керуючи життєвим циклом реплік і таблицями маршрутизації.

Ця довідка містить вичерпний опис схем, внутрішніх механізмів узгодження, параметрів аналізу та шаблонів запитів телеметрії для трьох провідних інструментів індустрії: **Argo Rollouts**, **Flagger** та **Envoy Proxy**.

---

## 1. Специфікація Argo Rollouts API (`argoproj.io/v1alpha1`)

Argo Rollouts надає користувацький ресурс `Rollout`, який виступає прямою заміною стандартного ресурсу `Deployment` у Kubernetes, доповнюючи його декларативними стратегіями прогресивної доставки.

Контролер Argo Rollouts керує двома підпорядкованими наборами реплік (`ReplicaSet`): стабільним (англ. *Stable ReplicaSet*), який виконує перевірену версію коду, та канарковим (англ. *Canary ReplicaSet*), що містить нову версію артефакту. На відміну від стандартного почергового оновлення Kubernetes, де трафік розподіляється пропорційно кількості подів, Argo Rollouts інтегрується безпосередньо з мережевим шаром Ingress або Service Mesh, дозволяючи виділити на нову версію, наприклад, 2% трафіку навіть за наявності лише одного канаркового пода серед сотні стабільних.

### Схема ресурсу `Rollout` з канарковою стратегією

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: payment-service-rollout
  namespace: production
  labels:
    app.kubernetes.io/name: payment-service
spec:
  replicas: 20
  revisionHistoryLimit: 5
  selector:
    matchLabels:
      app.kubernetes.io/name: payment-service
  strategy:
    canary:
      # Посилання на сервіси Kubernetes для маршрутизації
      canaryService: payment-service-canary
      stableService: payment-service-stable
      
      # Інтеграція з L7-маршрутизатором трафіку
      trafficRouting:
        nginx:
          stableIngress: payment-service-ingress
        # Альтернативно для Istio:
        # istio:
        #   virtualService:
        #     name: payment-virtual-service
        #     routes:
        #       - primary
        #   destinationRule:
        #     name: payment-destination-rule
        #     canarySubsetName: canary
        #     stableSubsetName: stable

      # Покроковий графік збільшення ваги трафіку
      steps:
        - setWeight: 2
        - pause: { duration: 10m }
        - setWeight: 10
        - pause: { duration: 15m }
        - setWeight: 25
        - pause: { duration: 30m }
        - setWeight: 50
        - pause: { duration: 30m }

      # Автоматизований фоновий аналіз метрик на кожному кроці
      analysis:
        templates:
          - templateName: payment-success-rate-analysis
          - templateName: payment-latency-p99-analysis
        args:
          - name: service-name
            value: payment-service
        maxWeight: 100
        stepWeight: 20

  template:
    metadata:
      labels:
        app.kubernetes.io/name: payment-service
    spec:
      containers:
        - name: server
          image: registry.internal/payment-service:v2.4.0
          ports:
            - containerPort: 8080
              name: http
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "2000m"
              memory: "2048Mi"
          readinessProbe:
            httpGet:
              path: /healthz/ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
```

---

### Механізм виконання канаркових кроків (`steps`) та аналізу

Коли в специфікації `Rollout` змінюється версія образу контейнера або конфігурація середовища, контролер запускає цикл прогресивної доставки:
1. Контролер створює новий об'єкт `ReplicaSet` для канарки і масштабує його до мінімальної кількості подів, необхідної для обслуговування першого кроку.
2. Виконується перший крок `setWeight: 2`: контролер патчить правила NGINX Ingress або Istio VirtualService, встановлюючи вагу маршруту на канарковий сервіс у розмірі 2%.
3. Настає фаза `pause: { duration: 10m }`: контролер блокує подальший рух за розкладом на 10 хвилин. Одночасно створюється екземпляр ресурсу `AnalysisRun`, який починає періодично опитувати сервери моніторингу за правилами, вказаними в `AnalysisTemplate`.
4. Якщо протягом 10 хвилин усі перевірки метрик повертають статус `Successful`, контролер переходить до кроку `setWeight: 10`, збільшуючи вагу та динамічно домасштабовуючи кількість реплік канарки.
5. Якщо хоча б одна метрика перевищує ліміт невдач `failureLimit`, `AnalysisRun` переходить у стан `Failed`. Контролер негайно перериває виконання кроків, обнуляє вагу маршрутизатора до 0% і масштабує канарковий `ReplicaSet` до нуля, відновлюючи 100% обслуговування стабільним кодом.

---

### Таблиця параметрів канаркової стратегії `spec.strategy.canary`

| Поле | Тип | Обов'язкове | Опис та рекомендації щодо використання |
|---|---|---|---|
| `canaryService` | `string` | Так | Ім'я об'єкта `Service` Kubernetes, що обирає поди нової канаркової версії. |
| `stableService` | `string` | Так | Ім'я об'єкта `Service` Kubernetes, що обирає поди стабільної версії `v1`. |
| `trafficRouting` | `object` | Ні | Конфігурація L7-провайдера (NGINX, Istio, AWS ALB, Ambassador, Traefik, SMI). |
| `steps` | `array` | Так | Послідовність кроків зміни ваги трафіку (`setWeight`) та пауз очікування (`pause`). |
| `steps[].setWeight` | `integer` | Ні | Відсоток вхідного трафіку для канарки (ціле число в діапазоні від 0 до 100). |
| `steps[].pause` | `object` | Ні | Час витримки (`duration: 10m`). Якщо `duration` не вказано, пауза вимагає ручного підтвердження оператором. |
| `steps[].setCanaryScale`| `object`| Ні | Явне масштабування реплік канарки (наприклад, `weight: 20` або `replicas: 3`). |
| `analysis` | `object` | Ні | Правила підключення фонового або синхронного аналізу через `AnalysisTemplate`. |
| `maxSurge` | `string/int` | Ні | Максимальна кількість додаткових подів понад норму під час релізу (за замовчуванням `"25%"`). |
| `maxUnavailable` | `string/int` | Ні | Максимально допустима кількість недоступних подів (за замовчуванням `0`). |
| `antiAffinity` | `object` | Ні | Правила розподілу подів між різними фізичними нодами кластера (Anti-Affinity). |

---

### Специфікація `AnalysisTemplate` (`argoproj.io/v1alpha1`)

Об'єкт `AnalysisTemplate` інкапсулює математичні правила запитів телеметрії, періодичність опитування, затримки прогріву та граничні умови провалу канарки:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: payment-success-rate-analysis
  namespace: production
spec:
  args:
    - name: service-name
  metrics:
    - name: success-rate
      interval: 1m
      initialDelay: 2m
      count: 10
      successCondition: result[0] >= 0.9990
      failureLimit: 2
      consecutiveErrorLimit: 3
      provider:
        prometheus:
          address: http://prometheus-server.monitoring.svc.cluster.local:9090
          query: |
            sum(rate(http_requests_total{app="{{args.service-name}}", status!~"5.*", variant="canary"}[1m]))
            /
            sum(rate(http_requests_total{app="{{args.service-name}}", variant="canary"}[1m]))

    - name: latency-p99
      interval: 1m
      initialDelay: 2m
      count: 10
      successCondition: result[0] <= 0.050
      failureLimit: 1
      provider:
        prometheus:
          address: http://prometheus-server.monitoring.svc.cluster.local:9090
          query: |
            histogram_quantile(0.99,
              sum(rate(http_request_duration_seconds_bucket{app="{{args.service-name}}", variant="canary"}[1m])) by (le)
            )
```

---

### Обробка збоїв моніторингу та параметри стійкості

При виконанні автоматизованого аналізу життєво важливо розрізняти реальний збій канаркового сервісу та тимчасову недоступність самої системи моніторингу (наприклад, перезавантаження сервера Prometheus чи мережевий таймаут API).

Для цього специфікація `AnalysisTemplate` підтримує два незалежні лічильники відмов:
* **`failureLimit`:** кількість випадків, коли запит до моніторингу повернув коректні дані, але значення метрики порушило умову `successCondition` (реальна деградація коду). Перевищення цього ліміту негайно ініціює аварійний відкіт.
* **`consecutiveErrorLimit`:** допустима кількість послідовних помилок з'єднання з провайдером метрик (HTTP 500, таймаути підключення, невалідний JSON). Якщо Prometheus не відповідає протягом двох ітерацій, контролер не перериває деплой панічно, а повторює спробу на наступній ітерації. Лише при стійкій відмові моніторингу (перевищенні `consecutiveErrorLimit`) реліз переходить у стан безпечного блокування.

---

### Таблиця параметрів метрик `spec.metrics[]` в `AnalysisTemplate`

| Поле | Тип | За замовчуванням | Опис |
|---|---|---|---|
| `name` | `string` | Обов'язкове | Унікальний ідентифікатор індикатора SLI всередині шаблону. |
| `interval` | `string` | Обов'язкове | Інтервал між повторними обчисленнями метрики (наприклад, `30s`, `1m`, `5m`). |
| `initialDelay` | `string` | `0s` | Затримка перед першим виконанням запиту для прогріву подів і JIT. |
| `count` | `integer` | Необмежено | Загальна кількість успішних перевірок, необхідних для завершення аналізу. |
| `successCondition` | `string` | Обов'язкове | Булевий вираз оцінки результату (наприклад, `result[0] >= 0.995`). |
| `failureLimit` | `integer` | `0` | Максимальна сумарна кількість провалів умови перед активацією відкату. |
| `consecutiveErrorLimit`| `integer`| `4` | Максимальна кількість послідовних помилок запиту до провайдера моніторингу. |
| `provider` | `object` | Обов'язкове | Джерело даних: `prometheus`, `datadog`, `newRelic`, `wavefront`, `web`. |

---

## 2. Специфікація Flagger Canary API (`flagger.app/v1beta1`)

Оператор Flagger реалізує повний життєвий цикл прогресивної доставки для стандартних об'єктів `Deployment` та `DaemonSet` у поєднанні з сервісними сітками (Istio, Linkerd, Gloo) або Ingress-контролерами.

На відміну від Argo Rollouts, Flagger не змінює тип базового ресурсу робочого навантаження: розробники продовжують створювати звичайні маніфести `Deployment`. Flagger перехоплює управління розгортанням, автоматично створюючи дублюючі об'єкти:
* **Primary Deployment (`<name>-primary`):** стабільний пул, що обслуговує основну масу користувачів.
* **Canary Deployment (`<name>`):** тестовий пул, куди розгортається новий реліз для аналізу.

### Схема ресурсу `Canary`

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: order-processor
  namespace: e-commerce
spec:
  # Цільовий об'єкт розгортання
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-processor

  # Посилання на горизонтальний автоскейлер
  autoscalerRef:
    apiVersion: autoscaling/v2
    kind: HorizontalPodAutoscaler
    name: order-processor-hpa

  # Конфігурація сервісу та маршрутизації
  service:
    port: 8080
    targetPort: http
    gateways:
      - mesh
      - public-gateway.istio-system.svc.cluster.local
    hosts:
      - orders.internal.domain
    trafficPolicy:
      tls:
        mode: ISTIO_MUTUAL

  # Розклад та метрики прогресивного аналізу
  analysis:
    interval: 1m
    threshold: 3
    maxWeight: 50
    stepWeight: 5
    stepWeightPromotion: 100
    
    # Критерії оцінки
    metrics:
      - name: request-success-rate
        thresholdRange:
          min: 99.5
        interval: 1m
      - name: request-duration
        thresholdRange:
          max: 150
        interval: 1m
      - name: custom-database-deadlocks
        templateRef:
          name: db-deadlocks-metric
          namespace: e-commerce
        thresholdRange:
          max: 0
        interval: 1m

    # Системні сповіщення та вебхуки
    webhooks:
      - name: pre-rollout-smoke-test
        type: pre-rollout
        url: http://load-tester.testing.svc.cluster.local/smoke
        timeout: 30s
        metadata:
          type: "smoke"
      - name: rollback-pagerduty-alert
        type: rollback
        url: http://alert-gateway.monitoring.svc.cluster.local/pagerduty
        timeout: 10s
        metadata:
          severity: "critical"
```

---

### Життєвий цикл узгодження Flagger та механіка вебхуків

Flagger керує станами розгортання через скінченний автомат: `Initializing` → `Waiting` → `Progressing` → `Promoting` → `Finalising` → `Succeeded` (або `Failed`).

Під час канаркового випуску оператор підтримує чотири фази виконання вебхуків:
1. **`pre-rollout`:** запускається перед тим, як на канарку буде спрямовано перший відсоток живого трафіку. Використовується для виконання димових тестів (Smoke Tests), перевірки доступності міграцій бази даних та прогріву кешів.
2. **`rollout`:** виконується паралельно з кожною ітерацією аналізу. Зазвичай викликає генератори синтетичного навантаження для забезпечення мінімального QPS на рідкісних маршрутах.
3. **`post-rollout`:** викликається після успішної промоції релізу на 100% трафіку для виконання очистки тимчасових ресурсів та закриття релізного тікета в системі відстеження завдань.
4. **`rollback`:** активується при фіксації деградації метрик для миттєвої відправки сповіщень черговій інженерній команді через системи PagerDuty, Slack або корпоративний Webhook.

---

### Таблиця параметрів аналізу Flagger `spec.analysis`

| Параметр | Тип | Рекомендоване значення | Опис призначення |
|---|---|---|---|
| `interval` | `string` | `1m` – `2m` | Періодичність ітерацій зважування та перевірки метрик. |
| `threshold` | `integer` | `3` – `5` | Кількість послідовних невдалих перевірок для ініціації відкату. |
| `maxWeight` | `integer` | `50` | Максимальний відсоток трафіку канарки перед повною промоцією. |
| `stepWeight` | `integer` | `2` – `10` | Крок приросту ваги канарки на кожній успішній ітерації. |
| `stepWeightPromotion` | `integer` | `100` | Крок збільшення ваги під час фінальної фази переходу на новий реліз. |
| `metrics[].name` | `string` | Вбудований / Custom | `request-success-rate`, `request-duration` або посилання на `MetricTemplate`. |
| `metrics[].thresholdRange`| `object`| `min`/`max` | Допустимий числовий діапазон значень (наприклад, `min: 99.0` для відсотка успіху). |

---

## 3. Конфігурація маршрутизації Envoy L7 (`envoy.config.route.v3`)

Сервісна сітка Envoy виконує динамічне зважування трафіку на основі об'єкта `RouteConfiguration` (xDS API v3), використовуючи зважені кластери `weighted_clusters`.

У розподіленій архітектурі Envoy взаємодіє з площиною управління (англ. *Control Plane*, наприклад Istio Pilot або власною реалізацією go-control-plane) за протоколами динамічного виявлення xDS:
* **LDS (Listener Discovery Service):** динамічно відкриває мережеві порти та прив'язує TLS-сертифікати.
* **RDS (Route Discovery Service):** оновлює правила маршрутизації та відсотки ваг без обриву існуючих TCP-з'єднань.
* **CDS (Cluster Discovery Service):** реєструє пули бекендів для версій `v1` та `v2`.
* **EDS (Endpoint Discovery Service):** передає точні списки IP-адрес і портів окремих подів.

### Приклад конфігурації маршрутизації Envoy VirtualHost

```yaml
virtual_hosts:
  - name: payment_vhost
    domains:
      - "payment.service.internal"
      - "10.96.0.45"
    routes:
      # Маршрут для внутрішнього тестування за HTTP-заголовком
      - match:
          prefix: "/"
          headers:
            - name: "X-Canary-Release"
              exact_match: "candidate"
        route:
          cluster: payment_service_canary_v2
          timeout: 5s

      # Основний зважений маршрут для користувачів
      - match:
          prefix: "/"
        route:
          weighted_clusters:
            clusters:
              - name: payment_service_stable_v1
                weight: 95
              - name: payment_service_canary_v2
                weight: 5
            total_weight: 100
            runtime_key_prefix: "routing.traffic_split.payment_service"
          timeout: 5s
          retry_policy:
            retry_on: "5xx,connect-failure,reset"
            num_retries: 2
            per_try_timeout: 1500ms
```

---

### Таблиця параметрів зваженої маршрутизації Envoy `weighted_clusters`

| Поле конфігурації | Тип | Опис та взаємодія з системою |
|---|---|---|
| `clusters[].name` | `string` | Назва цільового кластера бекендів (Upstream Cluster), визначеного в блоці `clusters`. |
| `clusters[].weight` | `UInt32Value` | Відносна вага кластера. Частка трафіку = `weight / total_weight`. |
| `total_weight` | `UInt32Value` | Сумарна вага всіх кластерів у групі (за замовчуванням `100`). |
| `runtime_key_prefix` | `string` | Префікс ключа в системі Envoy Runtime (RTDS) для динамічної зміни ваги без перезавантаження конфігурації. |

---

## 5. Просунуті патерни L7-маршрутизації: заголовки, куки та сесійна прив'язка

Крім простого відсоткового зважування, виробничі системи вимагають точкової сегментації клієнтського потоку на ранніх етапах релізу:

### Маршрутизація на основі HTTP-заголовків (Header-Based Routing)
На фазі нульового публічного відсотка (`0%` для звичайних користувачів) сервіс тестується внутрішніми командами розробки та QA. Шлюз налаштовується на перевірку специфічного HTTP-заголовка (наприклад, `X-Canary: candidate` або внутрішнього токена розробника). Усі запити з таким заголовком примусово спрямовуються на канарковий набір подів, тоді як 100% звичайних клієнтів продовжують обслуговуватися стабільною версією.

### Сесійна прив'язка за допомогою Cookie (Session Stickiness)
Якщо користувач потрапив на канарковий реліз на етапі 5% трафіку, балансувальник генерує сесійний cookie (наприклад, `canary-variant=candidate; Path=/; Max-Age=3600`). При наступних переходах по сторінках Ingress-контролер перевіряє наявність цього cookie і автоматично скеровує клієнта на ту саму версію. Це виключає розрив клієнтського стану під час багатоетапних дій (оформлення замовлення в кошику, проходження верифікації платежу).

---

## 7. Специфікація NGINX Ingress Controller Annotations

Для кластерів Kubernetes без встановленого Service Mesh зважена канаркова маршрутизація може бути налаштована через стандартний NGINX Ingress Controller за допомогою спеціальних анотацій:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: payment-ingress-canary
  namespace: production
  annotations:
    # Активація канаркового режиму
    nginx.ingress.kubernetes.io/canary: "true"
    
    # Відсоткове зважування (наприклад, 5% трафіку)
    nginx.ingress.kubernetes.io/canary-weight: "5"
    
    # Сегментація за HTTP-заголовком
    nginx.ingress.kubernetes.io/canary-by-header: "X-Canary-Test"
    nginx.ingress.kubernetes.io/canary-by-header-value: "always"
    
    # Сегментація за Cookie
    nginx.ingress.kubernetes.io/canary-by-cookie: "canary_user"
spec:
  ingressClassName: nginx
  rules:
    - host: payment.domain.internal
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: payment-service-canary
                port:
                  number: 8080
```

### Пріоритет обробки анотацій у NGINX Ingress
При одночасному оголошенні кількох правил Ingress-контролер NGINX застосовує таку сувору ієрархію пріоритетів:
1. `canary-by-header-value`: найвищий пріоритет. Якщо заголовок збігається зі значенням, запит завжди йде на канарку незалежно від інших правил.
2. `canary-by-header`: запит скеровується на канарку, якщо заголовок встановлено в `always`, і на стабільний бейзлайн, якщо в `never`.
3. `canary-by-cookie`: перевіряється значення сесійного cookie.
4. `canary-weight`: якщо жоден заголовок чи cookie не знайдено, застосовується загальне відсоткове зважування.

---

## 8. Специфікація Traefik Weighted Round Robin (WRR)

У хмарному шлюзі Traefik динамічний розподіл трафіку між двома бекендами реалізується за допомогою користувацького ресурсу `TraefikService` з типом `Weighted`:

```yaml
apiVersion: traefik.io/v1alpha1
kind: TraefikService
metadata:
  name: payment-wrr-service
  namespace: production
spec:
  weighted:
    services:
      - name: payment-service-stable
        port: 8080
        weight: 90
      - name: payment-service-canary
        port: 8080
        weight: 10
```

---

## 9. Специфікація AWS ALB Ingress Controller для канаркового зважування

У хмарній інфраструктурі AWS на базі Amazon EKS зважування канаркового трафіку на рівні Application Load Balancer (ALB) налаштовується через AWS Load Balancer Controller за допомогою спеціальних JSON-анотацій дії перенаправлення (Forward Action):

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: payment-alb-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/actions.canary-route: |
      {
        "Type": "forward",
        "ForwardConfig": {
          "TargetGroups": [
            {
              "ServiceName": "payment-service-stable",
              "ServicePort": "8080",
              "Weight": 95
            },
            {
              "ServiceName": "payment-service-canary",
              "ServicePort": "8080",
              "Weight": 5
            }
          ],
          "TargetGroupStickinessConfig": {
            "Enabled": true,
            "DurationSeconds": 3600
          }
        }
      }
spec:
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: canary-route
                port:
                  name: use-annotation
```

### Механіка взаємодії з AWS Target Group
AWS Load Balancer Controller автоматично транслює декларативну анотацію в конфігурацію двох незалежних цільових груп (Target Groups) на рівні AWS ALB API. Балансувальник здійснює апаратне зважування вхідних з'єднань із підтримкою сесійної фіксації (Stickiness), запобігаючи переходу користувачів між різними цільовими групами протягом однієї години.

---

## 10. Інтеграція зі сторонніми APM: провайдери Datadog та New Relic в Argo Rollouts

Крім Prometheus, контролер Argo Rollouts підтримує пряму інтеграцію з хмарними платформами моніторингу Application Performance Monitoring (APM):

### Провайдер Datadog в `AnalysisTemplate`
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: payment-datadog-analysis
  namespace: production
spec:
  metrics:
    - name: datadog-error-rate
      interval: 1m
      successCondition: default(result, 0) < 0.005
      failureLimit: 2
      provider:
        datadog:
          interval: 5m
          query: |
            avg:trace.http.request.errors{env:production,service:payment-service,version:v2}.as_rate()
            /
            avg:trace.http.request.hits{env:production,service:payment-service,version:v2}.as_rate()
```

### Провайдер Webhook для кастомних систем аналізу
Якщо організація використовує власну платформу оцінки релізів (наприклад, внутрішній сервіс валідації на базі машинного навчання), `AnalysisTemplate` дозволяє виконувати HTTP POST-запити:

```yaml
    - name: custom-ml-anomaly-detector
      interval: 2m
      successCondition: result.status == "healthy"
      provider:
        web:
          url: http://anomaly-detector.internal/api/v1/evaluate
          headers:
            - key: Authorization
              value: "Bearer {{secrets.ml-token}}"
          jsonPath: "{$.evaluation}"
```

---

## 11. Діагностика типових несправностей канаркового конвеєра

Під час експлуатації декларативних контролерів прогресивної доставки інженери стикаються з трьома основними класами збоїв інфраструктури аналізу:

### 1. Таймаути запитів до провайдера метрик (Metric Scrape Timeouts)
Якщо сервер Prometheus перевантажений великою кількістю одночасних аналізів, запит `AnalysisTemplate` може впасти за таймаутом. Щоб уникнути хибного відкату, встановлюють параметр `consecutiveErrorLimit: 3..5`. Контролер фіксує помилку зв'язку як технічний збій інфраструктури моніторингу (англ. *inconclusive trial*), не зараховуючи її як порушення бізнес-SLI самого релізу.

### 2. Затримка поширення конфігурації xDS (Control Plane Convergence Lag)
При зміні ваг у великих кластерах Envoy на тисячі вузлів оновлення конфігурації через протокол RDS/CDS вимагає від 100 до 500 мілісекунд для конвергенції. Якщо `AnalysisTemplate` починає збір метрик негайно в момент зміни ваги, перші вимірювання захоплять застарілий стан трафіку. Для нейтралізації цього ефекту в маніфестах обов'язково налаштовують `initialDelay: 30s..2m`.

### 3. Нерівномірність квантування часу PromQL (Step Jitter)
При розрахунку функцій `rate()` або `histogram_quantile()` діапазон вікна (наприклад, `[1m]`) повинен містити щонайменше 4 послідовні точки збору метрик. Якщо інтервал скрапінгу дорівнює 15 секунд, вікно менше `1m` призведе до появи порожніх проміжків (`NaN`), що спричинить хибний провал перевірки умови `successCondition`.

### 4. Конфлікти лімітів обчислювальних ресурсів (Resource Quota Exhaustion)
При створенні тимчасових канаркових та бейзлайн-подів сумарне споживання пам'яті та процесорних ядер у просторі імен зростає на `25–50%`. Якщо простір імен має жорстко встановлену квоту `ResourceQuota`, створення канаркових подів блокується планувальником Kubernetes зі статусом `FailedCreate`. Для запобігання збоям конвеєра простір імен повинен мати резервний запас лімітів квоти або налаштований параметр `maxSurge: "10%"`.





Перед тим, як відкрити реальний канарковий потік, сучасні Service Mesh дозволяють виконати дзеркалювання (асинхронне клонування) живих запитів за допомогою директиви Envoy `mirror_policy` або Istio `mirror`.

Шлюз дублює кожен вхідний HTTP-запит і надсилає його копію на канарковий сервіс у фоновому режимі. Відповіді канарки скидаються і не повертаються користувачеві, проте телеметрія канаркового процесу (навантаження на процесор, споживання пам'яті, частота внутрішніх винятків) фіксується системою моніторингу. Це дозволяє перевірити стабільність нового коду під повним бойовим навантаженням із нульовим радіусом ураження для клієнтів.


Для точного статистичного моніторингу запити Prometheus повинні обчислювати відносні показники окремо для міток `variant="canary"` та `variant="baseline"`.

При складанні запитів PromQL необхідно враховувати два критичні правила:
1. **Правило вікна швидкості (`rate window`):** вікно обчислення швидкості (наприклад, `[2m]`) повинно щонайменше вдвічі перевищувати інтервал опитування Prometheus (Scrape Interval), щоб виключити помилки через нерегулярний збір телеметрії.
2. **Фільтрація за мітками варіантів:** сервіси повинні експортувати мітку версії або варіанту безпосередньо в кожному HTTP-лічильнику для точного зіставлення когорт.

### 1. Частота помилок (Error Rate)
```promql
# Частка відповідей 5xx від загальної кількості запитів на канарці (від 0.0 до 1.0)
sum(rate(http_requests_total{app="payment", status=~"5.*", variant="canary"}[2m]))
/
sum(rate(http_requests_total{app="payment", variant="canary"}[2m]))
```

### 2. 99-й перцентиль затримки (p99 Latency)
```promql
# Розрахунок 99-го перцентиля затримки в секундах
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket{app="payment", variant="canary"}[2m])) by (le)
)
```

### 3. Диференційне порівняння частоти помилок (Canary vs Baseline Delta)
```promql
# Різниця частоти помилок між канаркою та бейзлайном
(
  sum(rate(http_requests_total{app="payment", status=~"5.*", variant="canary"}[2m]))
  /
  sum(rate(http_requests_total{app="payment", variant="canary"}[2m]))
)
-
(
  sum(rate(http_requests_total{app="payment", status=~"5.*", variant="baseline"}[2m]))
  /
  sum(rate(http_requests_total{app="payment", variant="baseline"}[2m]))
)
```

Ці специфікації та запити формують фундамент сучасної автоматизованої експлуатації, перетворюючи управління ризиками релізу на детермінований програмний контракт.
