# 📋 Декларативні специфікації та контракти стратегій розгортання

Декларативні специфікації розгортання є формальним контрактом між інженерною командою та платформою оркестрації, що описує бажаний кінцевий стан інфраструктури, допустимі межі тимчасової зміни ємності кластера, пороги автоматизованого аналізу телеметрії та процедури аварійного відкочування. Замість виконання послідовності імперативних скриптів адміністратор фіксує математичні обмеження у вигляді маніфестів, а контролер оркестрації (Kubernetes Deployment Controller, Argo Rollouts або Flagger) безперервно узгоджує поточний стан системи з описаним еталоном (англ. *reconciliation loop*).

Нижче наведено повний довідник структур даних, полів конфігурації, валідаційних правил та системних контрактів для стандартного механізму Kubernetes Deployment, розширених операторів прогресивної доставки та площин маршрутизації трафіку.

## Специфікація Kubernetes Deployment (`apps/v1`)

Об'єкт `Deployment` у Kubernetes керує життєвим циклом наборів реплік (`ReplicaSet`) та надає декларативні оновлення для безстанційних застосунків.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
  namespace: production
  labels:
    app.kubernetes.io/name: payment-service
    app.kubernetes.io/version: "2.4.0"
spec:
  replicas: 8
  revisionHistoryLimit: 10
  minReadySeconds: 30
  progressDeadlineSeconds: 600
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0
  selector:
    matchLabels:
      app: payment-service
  template:
    metadata:
      labels:
        app: payment-service
        version: "2.4.0"
    spec:
      terminationGracePeriodSeconds: 45
      containers:
        - name: app
          image: registry.example.com/payment:v2.4.0
          ports:
            - containerPort: 8080
          startupProbe:
            httpGet:
              path: /healthz/startup
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 2
            failureThreshold: 30
          readinessProbe:
            httpGet:
              path: /healthz/ready
              port: 8080
            initialDelaySeconds: 0
            periodSeconds: 5
            timeoutSeconds: 2
            successThreshold: 1
            failureThreshold: 2
          livenessProbe:
            httpGet:
              path: /healthz/live
              port: 8080
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
```

### Повний аналіз полів керування стратегією розгортання

1. **`spec.strategy.type` (рядок):** Визначає базовий алгоритм заміни екземплярів.
   * `RollingUpdate` (за замовчуванням): поступова поетапна заміна старих подів новими без зупинки всього сервісу. Забезпечує безперервну доступність системи для користувачів.
   * `Recreate`: повне примусове знищення всіх існуючих подів старої версії до того, як планувальник почне створювати перший под нової версії. Застосовується виключно тоді, коли дві версії застосунку категорично не можуть працювати одночасно через блокування бази даних або фізичні ресурси.

2. **`spec.strategy.rollingUpdate.maxSurge` (ціле число або відсоток):** Верхня межа допустимого перевищення кількості подів над цільовим числом `replicas`.
   * Якщо `replicas: 8` і `maxSurge: 25%`, контролер має право підняти до `8 + 2 = 10` подів одночасно.
   * Дробові значення завжди округлюються вгору до найближчого цілого числа.
   * Більше значення `maxSurge` прискорює процес розгортання, проте вимагає від кластера наявності достатнього запасу процесорних потужностей та оперативної пам'яті (англ. *resource headroom*).

3. **`spec.strategy.rollingUpdate.maxUnavailable` (ціле число або відсоток):** Максимальна кількість подів, які можуть перебувати в неробочому стані відносно бажаного числа `replicas`.
   * Значення `maxUnavailable: 0` встановлює жорстку гарантію: кластер за жодних умов не знищить старий под, поки новий под не доведе свою повну працездатність успішним проходженням `readinessProbe`.
   * Дробові значення завжди округлюються вниз. Одночасне встановлення `maxSurge: 0` та `maxUnavailable: 0` є невалідною конфігурацією, оскільки контролер не зможе ані створити новий под, ані видалити старий.

4. **`spec.minReadySeconds` (ціле число секунд):** Захисний часовий інтервал стабілізації.
   * За замовчуванням дорівнює `0`, що означає перехід до наступного кроку деплою негайно після першої ж успішної відповіді `readinessProbe`.
   * Встановлення значення `minReadySeconds: 30` змушує контролер спостерігати за новим подом протягом 30 секунд. Якщо протягом цього вікна процес зазнає падіння (англ. *crash*), оновлення зупиняється, що запобігає знищенню старого працюючого пулу.

5. **`spec.progressDeadlineSeconds` (ціле число секунд):** Бюджет часу на виконання всього процесу оновлення.
   * Якщо через помилки завантаження образу (`ImagePullBackOff`), брак ресурсів вузлів або нескінченні падіння контейнерів оновлення не завершується за вказаний час, контролер фіксує аварійний стан `ProgressDeadlineExceeded` у статусі об'єкта.

6. **`spec.revisionHistoryLimit` (ціле число):** Глибина збереження історії `ReplicaSet`.
   * Визначає кількість збережених старих маніфестів для забезпечення миттєвого відкочування (`kubectl rollout undo`). Занадто велике значення засмічує базу даних `etcd` кластера метаданими неактивних ресурсів.

7. **`spec.template.spec.terminationGracePeriodSeconds` (ціле число секунд):** Тайм-аут коректного завершення роботи процесу.
   * Часовий проміжок між надсиланням сигналу `SIGTERM` та примусовим знищенням процесу сигналом `SIGKILL`. За цей час застосунок повинен коректно завершити активні клієнтські HTTP-з'єднання та закрити дескриптори бази даних.

8. **`spec.paused` (булеве):** Прапорець ручного призупинення оновлення.
   * Встановлення значення `true` (через маніфест або команду `kubectl rollout pause`) заморожує будь-які зміни в `ReplicaSet`. Це дозволяє інженерам внести серію правок (змінити змінні середовища, конфігураційні карти, ліміти пам'яті та образ) і застосувати їх одночасно однією транзакцією через `kubectl rollout resume`, уникаючи проміжних непотрібних хвиль перезапуску.

### Механіка узгодження зондів працездатності (Probe Reconciliation Contract)

Оркестратор координує маршрутизацію трафіку та перемикання життєвого циклу контейнера за допомогою трьох спеціалізованих зондів:

* **Зонд початкового запуску (`startupProbe`):** призначений для систем із тривалою фазою ініціалізації (прогрів JIT-компілятора, завантаження моделей машинного навчання в GPU, створення пулів з'єднань). Поки `startupProbe` не поверне успіх, виконання перевірок `livenessProbe` та `readinessProbe` примусово блокується. Якщо час, визначений добутком `failureThreshold * periodSeconds`, вичерпано без успіху, контейнер знищується.
* **Зонд готовності (`readinessProbe`):** єдиний зонд, який безпосередньо взаємодіє з мережевими балансувальниками (`Endpoints` та `EndpointSlice`). Успішна відповідь включає IP-адресу пода в маршрутні таблиці `kube-proxy` та Ingress-контролерів. Провал зонда негайно видаляє под зі списку активних цілей без перезапуску контейнера.
* **Зонд живучості (`livenessProbe`):** контролює факт нормального функціонування процесу. Виявляє внутрішні зависання (deadlock потоків, вичерпання пулу з'єднань), за яких вебсервер перестає відповідати. При багаторазовому провалі перевірки середовище виконання контейнерів перезапускає процес.

## Специфікація Argo Rollouts (`argoproj.io/v1alpha1`)

Оператор Argo Rollouts надає повноцінний контролер прогресивної доставки, що підтримує синьо-зелені перемикання, багатоступеневі канаркові релізи та інтегрований аналіз метрик.

### Синьо-зелена специфікація (Blue-Green)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: order-processor
  namespace: production
spec:
  replicas: 10
  revisionHistoryLimit: 5
  selector:
    matchLabels:
      app: order-processor
  strategy:
    blueGreen:
      activeService: order-processor-active
      previewService: order-processor-preview
      autoPromotionEnabled: false
      autoPromotionSeconds: 300
      scaleDownDelaySeconds: 600
      prePromotionAnalysis:
        templates:
          - templateName: smoke-tests
      postPromotionAnalysis:
        templates:
          - templateName: error-rate-analysis
  template:
    metadata:
      labels:
        app: order-processor
    spec:
      containers:
        - name: app
          image: registry.example.com/order-processor:v3.1.0
          ports:
            - containerPort: 8080
```

#### Повний опис полів Blue-Green стратегії

* `activeService` (рядок): посилання на сервіс Kubernetes, що приймає 100% живого виробничого трафіку користувачів. Контролер спрямовує селектор цього сервісу на стабільний набір реплік (Blue).
* `previewService` (рядок): посилання на виділений прев'ю-сервіс, підключений виключно до нового набору реплік (Green). Дозволяє виконувати синтетичне тестування та перевірку працездатності нового коду до перемикання користувачів.
* `autoPromotionEnabled` (булеве): керує автоматизацією фінального перемикання. Якщо встановлено значення `false`, контролер призупиняє реліз після розгортання Green-пулу й очікує ручної команди інженера `kubectl argo rollouts promote` або виклику зовнішнього API.
* `autoPromotionSeconds` (ціле число): автоматичний таймер витримки. Якщо протягом зазначеного інтервалу не надійшло сигналів про помилки, контролер самостійно виконує перемикання активного сервісу.
* `scaleDownDelaySeconds` (ціле число): критичний параметр безпеки, що визначає, скільки секунд старий пул (Blue) залишатиметься запущеним після перемикання трафіку на Green. Якщо протягом перших 10 хвилин виявиться критична помилка, контролер виконує миттєве зворотне перемикання селектора `activeService` на існуючий Blue-пул без затримки на створення нових контейнерів.
* `prePromotionAnalysis` (об'єкт): декларативний блок запуску перевірок працездатності на `previewService` перед перемиканням трафіку.
* `postPromotionAnalysis` (об'єкт): безперервний статистичний контроль метрик після перемикання живого трафіку на новий сервіс.

### Канаркова специфікація з кроками та шлюзом NGINX

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: catalog-api
  namespace: production
spec:
  replicas: 20
  strategy:
    canary:
      canaryService: catalog-api-canary
      stableService: catalog-api-stable
      trafficRouting:
        nginx:
          stableIngress: catalog-api-ingress
      steps:
        - setWeight: 5
        - pause: { duration: 15m }
        - analysis:
            templates:
              - templateName: prometheus-error-rate
            args:
              - name: service-name
                value: catalog-api
        - setWeight: 20
        - pause: { duration: 30m }
        - setWeight: 50
        - pause: { duration: 1h }
  template:
    metadata:
      labels:
        app: catalog-api
    spec:
      containers:
        - name: app
          image: registry.example.com/catalog:v2.0.1
```

#### Анатомія кроків канаркового розгортання (`steps`)

1. **`setWeight` (ціле число від 0 до 100):** встановлює відсоток вхідного трафіку, який Ingress-контролер або Service Mesh повинен спрямувати на канарковий набір реплік.
2. **`pause` (об'єкт):** призупиняє виконання плану розгортання на заданий інтервал часу (`duration: 15m`) або до ручного підтвердження оператором (якщо поле `duration` не вказано).
3. **`analysis` (об'єкт):** ініціює запуск фонового аналізу метрик за допомогою зазначеного `AnalysisTemplate`. Якщо аналіз завершується невдачею, контролер скасовує подальше просування і запускає автоматичний відкіт.

### Контракт автоматизованого аналізу метрик (`AnalysisTemplate`)

Об'єкт `AnalysisTemplate` описує правила вибірки телеметрії та математичні критерії оцінки успішності канаркового випуску.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: prometheus-error-rate
  namespace: production
spec:
  args:
    - name: service-name
  metrics:
    - name: success-rate
      interval: 1m
      count: 10
      successCondition: result[0] >= 0.995
      failureLimit: 2
      provider:
        prometheus:
          address: http://prometheus-k8s.monitoring.svc:9090
          query: |
            sum(rate(http_requests_total{service="{{args.service-name}}", status!~"5.*"}[2m]))
            /
            sum(rate(http_requests_total{service="{{args.service-name}}"}[2m]))
    - name: p99-latency
      interval: 1m
      count: 5
      successCondition: result[0] <= 0.150
      failureLimit: 1
      provider:
        prometheus:
          address: http://prometheus-k8s.monitoring.svc:9090
          query: |
            histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{service="{{args.service-name}}"}[2m])) by (le))
```

#### Довідник полів AnalysisTemplate

* `metrics.interval` (рядок часу): періодичність виконання запиту до бази даних моніторингу (наприклад, кожні `1m` або `30s`).
* `metrics.count` (ціле число): загальна кількість успішних ітерацій замірів, необхідних для визнання аналізу пройденим.
* `metrics.successCondition` (логічний вираз): правило валідації поверненого значення. Змінна `result[0]` містить скалярний результат виконання PromQL-запиту.
* `metrics.failureLimit` (ціле число): максимальна кількість невдалих вимірів (коли умова успішності не виконана), після якої весь аналіз отримує статус `Failed`, що ініціює аварійний відкіт розгортання.
* `metrics.provider` (об'єкт): драйвер підключення до системи збору метрик. Підтримує Prometheus, Datadog, New Relic, AWS CloudWatch, Wavefront або довільні HTTP Webhook ендпоінти.

## Специфікація Flagger (`flagger.app/v1beta1`)

Оператор Flagger автоматизує процес прогресивного розгортання, самостійно генеруючи об'єкти `Deployment-primary` та `Deployment-canary` на основі цільового референсу.

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: user-auth
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: user-auth
  service:
    port: 8080
    targetPort: 8080
    gateways:
      - mesh
      - public-gateway.istio-system.svc.cluster.local
    hosts:
      - auth.example.com
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
      - name: request-success-rate
        thresholdRange:
          min: 99
        interval: 1m
      - name: request-duration
        thresholdRange:
          max: 500
        interval: 1m
    webhooks:
      - name: acceptance-test
        type: pre-rollout
        url: http://flagger-loadtester.test/
        timeout: 30s
        metadata:
          type: bash
          cmd: "curl -sd 'test' http://user-auth-canary:8080/healthz"
      - name: load-test
        type: rollout
        url: http://flagger-loadtester.test/
        timeout: 5s
        metadata:
          cmd: "hey -z 1m -q 100 -c 2 http://user-auth-canary:8080/auth"
```

### Поля конфігурації Flagger Canary

* `targetRef`: посилання на базовий об'єкт `Deployment`, `DaemonSet` або `StatefulSet`, який Flagger бере під своє управління.
* `analysis.interval`: інтервал між кроками інкременту ваги та перевірки метрик.
* `analysis.threshold`: кількість послідовних збоїв перевірки метрик до початку автоматичного відкочування.
* `analysis.maxWeight`: максимальний відсоток трафіку, який дозволено виділити на канарковий екземпляр перед фінальним перемиканням.
* `analysis.stepWeight`: крок збільшення ваги на кожній успішній ітерації (наприклад, `10%` збільшує частку трафіку як `0% → 10% → 20% → 30% → 40% → 50%`).
* `webhooks`: інтеграційні хуки для виконання навантажувальних тестів, оповіщень у корпоративні месенджери та перевірки зовнішніх шлюзів безпеки.

## Контракти маршрутизації Service Mesh (Istio VirtualService & DestinationRule)

Для тонкого керування вагою трафіку на рівні L7 проксі-сайдкарів (Envoy) застосовується зв'язка двох декларативних ресурсів: `VirtualService` та `DestinationRule`.

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: billing-destinations
  namespace: production
spec:
  host: billing-service
  subsets:
    - name: stable
      labels:
        version: v1.8.0
    - name: canary
      labels:
        version: v1.9.0
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: billing-routing
  namespace: production
spec:
  hosts:
    - billing-service
  http:
    - route:
        - destination:
            host: billing-service
            subset: stable
          weight: 90
        - destination:
            host: billing-service
            subset: canary
          weight: 10
      timeout: 5s
      retries:
        attempts: 3
        perTryTimeout: 1s
        retryOn: "5xx,connect-failure,refused-stream"
```

### Специфікація тіньового клонування (Traffic Mirroring / Dark Launch)

Для перевірки нового коду в режимі повного темного запуску без впливу на користувачів використовується директива `mirror`:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: payment-mirror-routing
  namespace: production
spec:
  hosts:
    - payment-service
  http:
    - match:
        - uri:
            prefix: /api/v1/charge
      route:
        - destination:
            host: payment-service
            subset: stable
          weight: 100
      mirror:
        host: payment-service
        subset: canary
      mirrorPercentage:
        value: 100.0
```

У такій конфігурації клієнт отримує 100% відповідей від стабільного пулу `stable`, а Envoy асинхронно створює точну копію вхідного запиту та направляє її до тіньового кандидата `canary`, відкидаючи його відповіді на мережевому рівні.

## Специфікації розгортання в AWS ECS, Knative та OpenShift

Окрім класичного Kubernetes, сучасні хмарні платформи надають власні спеціалізовані моделі декларативного розгортання:

### 1. Специфікація AWS ECS Service (Rolling vs CodeDeploy Blue/Green)
У платформі Amazon Elastic Container Service (ECS) керування почерговим оновленням описується через параметри відносної ємності:
* `minimumHealthyPercent` (за замовчуванням 100%): аналог `100% - maxUnavailable`. Встановлення значення 100% забороняє зупинку старих завдань до запуску нових.
* `maximumPercent` (за замовчуванням 200%): аналог `100% + maxSurge`. Дозволяє тимчасово подвоїти кількість запущених контейнерів на час оновлення.
* Інтеграція з AWS CodeDeploy дозволяє декларативно перемикати цільові групи балансувальника Application Load Balancer (ALB) між двома Target Groups (`TargetGroupPairInfo`) за заздалегідь визначеною лінійною або канарковою кривою (`Linear10PercentEvery1Minute` чи `Canary10Percent5Minutes`).

### 2. Специфікація Knative Serving (Безсерверне розщеплення трафіку)
У безсерверних середовищах (FaaS) кожна зміна коду або конфігурації автоматично породжує незмінний знімок (англ. *Revision*). Маршрутизація трафіку описується через масив `spec.traffic` в об'єкті `Service`:

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: invoice-generator
  namespace: production
spec:
  template:
    metadata:
      name: invoice-generator-v2
  traffic:
    - tag: current
      revisionName: invoice-generator-v1
      percent: 80
    - tag: candidate
      revisionName: invoice-generator-v2
      percent: 20
```

Поле `tag` створює виділені прев'ю-домени (наприклад, `candidate-invoice-generator.example.com`), які дозволяють виконувати адресне тестування нової ревізії безпосередньо через браузер перед відкриттям основного трафіку.

### 3. OpenShift DeploymentConfig і життєвий цикл гачків (Lifecycle Hooks)
У платформі Red Hat OpenShift об'єкт `DeploymentConfig` підтримує виконання декларативних гачків (англ. *lifecycle hooks*) на ключових стадіях оновлення:

* `pre`: запуск міграцій бази даних або оновлення схем перед стартом першого нового контейнера. При невдачі скрипта розгортання скасовується без змін у працюючому пулі.
* `mid`: виконання проміжних перевірок та прогріву під час почергового оновлення.
* `post`: виконання сповіщень, інвалідів зовнішніх CDN-кешів або оновлення реєстрів сервісів після успішного завершення переходу.

## Систематика помилок конфігурації та методи діагностики

1. **Конфлікт `maxSurge` та квот ресурсів (Resource Quota Deadlock):** Якщо значення `maxSurge` вимагає створення 4 нових подів, але простір імен кластера (`ResourceQuota`) має ліміт пам'яті лише на 2 додаткові поди, створення нових контейнерів блокується планувальником Kubernetes з подією `FailedCreate: pods is forbidden: exceeded quota`. При цьому старі поди не видаляються через обмеження `maxUnavailable: 0`. Оновлення назавжди зависає у стані блокування до збільшення квоти або коригування параметрів розгортання.
2. **Мерехтіння готовності (Flapping Readiness Probe):** Якщо новий код відчуває дефіцит пам'яті або високу затримку збирача сміття під навантаженням, перевірка `/healthz/ready` може поперемінно повертати успіх і помилку. Це змушує Ingress-контролер хаотично додавати та видаляти под із балансування, викликаючи серію помилок 502/503 у клієнтів.
3. **Розсинхронізація селекторів сервісу (Orphaned ReplicaSet):** Зміна міток `spec.selector.matchLabels` у вже існуючому об'єкті Deployment призводить до втрати зв'язку між контролером та старими `ReplicaSet`, перетворюючи працюючі поди на некеровані зомбі-процеси.
4. **Тайм-аут виклику Prometheus (Analysis Query Timeout):** Якщо запит у `AnalysisTemplate` містить неоптимальні регулярні вирази або охоплює занадто великий часовий діапазон без агрегації індексів, сервер Prometheus повертає HTTP 504 Gateway Timeout. Контролер фіксує це як збій ініціалізації метрик і може помилково запустити аварійний відкіт розгортання через перевищення ліміту `failureLimit`.
5. **Розсинхронізація тайм-аутів завершення (Graceful Shutdown Race):** Якщо параметр `terminationGracePeriodSeconds` у специфікації пода (наприклад, 30 секунд) менший за час, необхідний довготривалим HTTP-запитам на завершення (наприклад, генерація PDF-звітів триває 45 секунд), процес буде примусово вбитий сигналом `SIGKILL`, що викличе обрив з'єднання та помилку на стороні клієнта.
6. **Залипання стану оновлення (Stalled Generation Mismatch):** Якщо поле `status.observedGeneration` менше за `metadata.generation`, це означає, що контролер ще не встиг опрацювати останню зміну специфікації. Спроба виконати повторний виклик оновлення під час активної фази узгодження призводить до накопичення черги запитів в API-сервері та деградації швидкодії площини керування.
