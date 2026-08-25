# 📋 Специфікація інтерфейсів та конфігурацій синьо-зеленого розгортання: Argo Rollouts, Envoy xDS та HAProxy Runtime API

Практична реалізація синьо-зеленого розгортання в сучасних розподілених системах вимагає узгодженої взаємодії кількох незалежних інфраструктурних шарів: декларативних контролерів оркестрації, динамічних L7-балансувальників трафіку та систем автоматизованого збору телеметрії. Кожен із цих компонентів функціонує на основі власних специфікацій, структур конфігурації та протоколів керування.

Головна вимога до інтерфейсів синьо-зеленого розгортання полягає в забезпеченні абсолютної передбачуваності та атомарності переходів. Будь-яка зміна маршрутизації, оновлення ваг чи виведення вузлів з експлуатації повинні виконуватися без розриву активних клієнтських сесій, без появи станів перегонів у мережевих таблицях та з можливістю миттєвого програмного відкату на попередню стабільну конфігурацію.

Нижче наведено вичерпний інженерний довідник структур даних, полів конфігурації, команд сокетів керування та контрактів автоматизованого аналізу для провідних технологій індустрії: Kubernetes-контролера *Argo Rollouts*, хмарного проксі *Envoy*, балансувальника високого навантаження *HAProxy* та хмарного API *AWS ALB Target Groups*.

## 1. Специфікація маніфесту Argo Rollouts (CRD: `argoproj.io/v1alpha1`)

Контролер Argo Rollouts розширює стандартне API Kubernetes користувацьким ресурсом `Rollout`, який замінює базовий об'єкт `Deployment` і надає декларативне керування синьо-зеленою стратегією. Замість того, щоб по черзі перезапускати поди в межах одного пулу, контролер створює два паралельні об'єкти `ReplicaSet` і керує селекторами міток у двох незалежних об'єктах `Service`.

Головний інваріант полягає в тому, що активна служба `activeService` завжди вказує на перевірений і стабільний `ReplicaSet`, тоді як прев'ю-служба `previewService` динамічно зв'язується з новим `ReplicaSet`, дозволяючи проводити димові тести, синтетичний прогрів кешів та верифікацію зондів готовності без спрямування користувацького трафіку.

### Анатомія конфігураційного блоку `spec.strategy.blueGreen`

Поведінка синьо-зеленого розгортання повністю визначається параметрами секції `blueGreen`. Кожен параметр відповідає за окремий етап життєвого циклу релізу.

| Поле | Тип | За замовчуванням | Обов'язкове | Призначення та поведінковий ефект |
| :--- | :--- | :--- | :--- | :--- |
| `activeService` | `string` | — | **Так** | Ім'я об'єкта `Service`, селектор якого контролер динамічно перемикає на `ReplicaSet` із 100% публічного трафіку. |
| `previewService` | `string` | — | Ні | Ім'я службового об'єкта `Service`, призначеного виключно для внутрішнього тестування, прогріву та валідації пасивного `ReplicaSet`. |
| `autoPromotionEnabled` | `boolean` | `true` | Ні | Якщо `false`, контролер зупиняє розгортання після проходження димових тестів і чекає на ручне підтвердження оператора (`kubectl argo rollouts promote`). |
| `autoPromotionSeconds` | `integer` | `0` | Ні | Часова затримка в секундах перед автоматичним перемиканням селектора активної служби після успішного проходження аналізу. |
| `scaleDownDelaySeconds` | `integer` | `30` | Ні | Тривалість періоду вистоювання (Standby Soak) у секундах. Визначає, скільки часу старий `ReplicaSet` залишається увімкненим для миттєвого відкату перед масштабуванням реплік до `0`. |
| `previewReplicaCount` | `integer` | К-сть `replicas` | Ні | Кількість реплік, що підіймаються у пасивному контурі для прогріву. Дозволяє економити ресурси, якщо для тестів не потрібен повний розмір кластера. |
| `maxUnavailable` | `integer \| string` | `0` | Ні | Максимальна кількість або відсоток подів, які можуть бути недоступними під час оновлення. Для строгого синьо-зеленого деплою фіксується як `0`. |
| `prePromotionAnalysis` | `object` | — | Ні | Посилання на шаблон аналізу (`AnalysisTemplate`), який виконує автоматичну верифікацію метрик Prometheus перед перемиканням трафіку. |
| `postPromotionAnalysis` | `object` | — | Ні | Шаблон аналізу, який контролює якість роботи нового релізу вже під живим трафіком протягом вікна `scaleDownDelaySeconds`. |
| `antiAffinity` | `object` | — | Ні | Правила розміщення подів, які запобігають розміщенню синіх і зелених подів на одних і тих самих фізичних вузлах Kubernetes для ізоляції відмов. |

### Механіка узгодження стану та автоматизованого аналізу

Цикл узгодження контролера Argo Rollouts (англ. *reconciliation loop*) безперервно відстежує стан подів у цільовому та активному `ReplicaSet`. Коли розробник оновлює поле `spec.template.spec.containers[0].image`, контролер виконує наступну послідовність дій:

1. **Генерація унікального PodTemplateHash:** контролер обчислює хеш нової специфікації та створює новий об'єкт `ReplicaSet` із відповідною міткою (наприклад, `rollouts-pod-template-hash=6f8d9b4c7`).
2. **Масштабування цільового пулу:** новий `ReplicaSet` масштабується до значення `previewReplicaCount` (або до повної кількості `replicas`).
3. **Зв'язування з прев'ю-службою:** селектор об'єкта `previewService` оновлюється хешем нового `ReplicaSet`. Вхідний тестовий трафік починає надходити на нові поди.
4. **Запуск аналізу Pre-Promotion:** створюється користувацький ресурс `AnalysisRun` на основі шаблону `prePromotionAnalysis`. Контролер виконує вказані у шаблоні PromQL-запити до Prometheus через регулярні проміжки часу `interval`.
5. **Атомарне перемикання:** після успішного завершення всіх ітерацій аналізу контролер оновлює селектор об'єкта `activeService`, підставляючи хеш нового `ReplicaSet`. 100% публічного трафіку миттєво переводиться на новий реліз.
6. **Вистоювання та масштабування до нуля:** старий `ReplicaSet` залишається увімкненим протягом періоду `scaleDownDelaySeconds`. Якщо протягом цього вікна активується пост-промоушн аналіз або надходить команда аварійного відкату, контролер повертає селектор `activeService` на старий хеш без повторного створення контейнерів. Після вичерпання таймера старий `ReplicaSet` масштабується до 0 реплік.

Життєвий гачок `preStop` у специфікації контейнера гарантує усунення стану перегонів при оновленні мережевих маршрутних таблиць. Коли под отримує команду на завершення роботи, команда `sleep 10` затримує відправку сигналу `SIGTERM` головному процесу на 10 секунд. Це дає системним компонентам `kube-proxy` та Ingress-контролерам достатній час, щоб оновити об'єкти `EndpointSlice` та вилучити IP-адресу вузла з усіх балансувальників до того, як сокет застосунку припинить слухати вхідні запити.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: payment-processing-engine
  namespace: production
  labels:
    app.kubernetes.io/name: payment-engine
    app.kubernetes.io/part-of: core-banking
spec:
  replicas: 10
  revisionHistoryLimit: 5
  selector:
    matchLabels:
      app: payment-engine
  template:
    metadata:
      labels:
        app: payment-engine
    spec:
      containers:
      - name: engine
        image: registry.internal/banking/payment-engine:v2.4.0
        ports:
        - name: http
          containerPort: 8080
          protocol: TCP
        resources:
          requests:
            cpu: "1000m"
            memory: "2Gi"
          limits:
            cpu: "2000m"
            memory: "4Gi"
        readinessProbe:
          httpGet:
            path: /healthz/ready
            port: http
          initialDelaySeconds: 5
          periodSeconds: 3
          timeoutSeconds: 2
          successThreshold: 1
          failureThreshold: 3
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 10"]
  strategy:
    blueGreen:
      activeService: payment-engine-active
      previewService: payment-engine-preview
      autoPromotionEnabled: true
      autoPromotionSeconds: 0
      scaleDownDelaySeconds: 600
      previewReplicaCount: 10
      antiAffinity:
        preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          podAffinityTerm:
            labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values: ["payment-engine"]
            topologyKey: "kubernetes.io/hostname"
      prePromotionAnalysis:
        templates:
        - templateName: verify-smoke-and-latency
        args:
        - name: service-name
          value: payment-engine-preview.production.svc.cluster.local
---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: verify-smoke-and-latency
  namespace: production
spec:
  args:
  - name: service-name
  metrics:
  - name: success-rate
    interval: 10s
    count: 3
    successCondition: result[0] >= 0.999
    failureLimit: 1
    provider:
      prometheus:
        address: http://prometheus-k8s.monitoring.svc:9090
        query: |
          sum(rate(http_requests_total{job="payment-engine",service="{{args.service-name}}",status!~"5.*"}[1m]))
          /
          sum(rate(http_requests_total{job="payment-engine",service="{{args.service-name}}"}[1m]))
  - name: p99-latency
    interval: 10s
    count: 3
    successCondition: result[0] <= 0.080
    failureLimit: 1
    provider:
      prometheus:
        address: http://prometheus-k8s.monitoring.svc:9090
        query: |
          histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{job="payment-engine",service="{{args.service-name}}"}[1m])) by (le))
```

---

## 2. Динамічна конфігурація Envoy xDS (RDS / EDS)

Envoy керує маршрутизацією на рівні шару L7 через конфігурацію маршрутів (Route Configuration) та кластерів бекендів (Clusters). Перемикання виконується атомарною зміною структури `weighted_clusters` або заміною цільового кластера в об'єкті маршруту.

На відміну від традиційних проксі-серверів, що вимагають перезачитування конфігураційних файлів на диску з перезапуском робочих процесів, архітектура Envoy базується на сервісах динамічного виявлення (англ. *Discovery Services*, xDS). Контролер публікує нову версію конфігурації через gRPC-канал, і Envoy застосовує її в оперативній пам'яті за частки мілісекунди без скидання з'єднань і без блокування мережевих потоків.

Модель конфігурації Envoy складається з чотирьох взаємопов'язаних рівнів абстракції:
1. **Слухачі (Listeners / LDS):** мережеві сокети, що приймають TCP-з'єднання від клієнтів (порти 80/443), завершують сесії TLS та передають потік байтів у ланцюжок фільтрів (HTTP Connection Manager).
2. **Маршрутизація (Route Configuration / RDS):** правила зіставлення віртуальних хостів (Virtual Hosts) та шляхів запитів (Path Prefixes) із цільовими кластерами бекендів.
3. **Кластери (Clusters / CDS):** логічні групи серверів однакового призначення (наприклад, `service_blue` та `service_green`) із власними політиками балансування, зондування працездатності та тайм-аутів.
4. **Кінцеві точки (Endpoints / EDS):** динамічні списки конкретних IP-адрес і портів окремих подів чи віртуальних машин у межах кластера.

### Таблиця параметрів Envoy для синьо-зеленого перемикання

| Поле в API Envoy | Тип | Опис та системна поведінка |
| :--- | :--- | :--- |
| `route.cluster` | `string` | Фіксоване ім'я цільового кластера бекендів (`service_blue` або `service_green`). Атомарно підміняється через RDS. |
| `route.weighted_clusters` | `object` | Дозволяє задавати точні цілочисельні ваги (наприклад, `blue: 0, green: 100`) без розриву активних з'єднань. |
| `common_http_protocol_options.max_connection_duration` | `duration` | Максимальний час життя TCP-з'єднання (наприклад, `300s`). Змушує довгоживучі сесії плавно перезакриватися. |
| `drain_time` | `duration` | Час, протягом якого Envoy надсилає кадри HTTP/2 `GOAWAY` старим клієнтам перед закриттям сокетів (наприклад, `30s`). |
| `health_checks.interval` | `duration` | Частота активного зондування бекендів (наприклад, `1s` під час фази прев'ю-тестів). |

### Обробка мультиплексованих протоколів HTTP/2 та gRPC

Для протоколів HTTP/2 та gRPC зміна ваг кластерів у структурі `weighted_clusters` відбувається на рівні окремих логічних запитів (фреймів `HEADERS`), а не на рівні фізичних TCP-сокетів. Це означає, що клієнт, який утримує єдине постійне TCP-з'єднання з проксі, відправлятиме перші запити на `service_blue`, а наступні запити в межах того самого з'єднання підуть на `service_green` одразу після оновлення версії маршруту.

Якщо ж необхідно повністю перевідкрити клієнтські сесії на рівні операційної системи, параметр `drain_time` активує надсилання керівного кадру `GOAWAY`. Проксі повідомляє клієнту, що поточні активні потоки будуть коректно завершені, проте для надсилання будь-яких наступних RPC-викликів клієнт зобов'язаний ініціювати нову сесію рукостискання TLS.

Крім того, Envoy підтримує політики повторних спроб `retry_policy`. Якщо під час перемикання на нове зелене середовище поодинокий запит стикається з відмовою підключення (`connect-failure`) або скиданням стріму (`refused-stream`), проксі прозоро для клієнта перенаправляє запит на резервний вузол, забезпечуючи нульову видимість мережевих сплесків для кінцевого користувача.

Важливим аспектом конфігурації є також вибір алгоритму балансування кластера (`lb_policy`). Для типових синьо-зелених контурів використовується політика `ROUND_ROBIN` або `LEAST_REQUEST`, тоді як для сервісів із локальними кешами в пам'яті доцільно застосовувати `RING_HASH` або `MAGLEV` на основі заголовка користувача чи куки для мінімізації промахів кешу під час перемикання.

```yaml
version_info: "v2"
resources:
- "@type": type.googleapis.com/envoy.config.route.v3.RouteConfiguration
  name: dynamic_production_routes
  virtual_hosts:
  - name: payment_api_vhost
    domains: ["api.payments.internal", "payments.company.com"]
    routes:
    - match:
        prefix: "/api/v1"
      route:
        # Атомарне перемикання: 100% трафіку переведено на кластер service_green
        weighted_clusters:
          clusters:
          - name: service_blue
            weight: 0
          - name: service_green
            weight: 100
          total_weight: 100
        timeout: 15s
        retry_policy:
          retry_on: "5xx,connect-failure,refused-stream"
          num_retries: 3
    - match:
        prefix: "/preview/api/v1"
      route:
        cluster: service_green
        timeout: 30s
```

---

## 3. Протокол керування HAProxy Runtime Socket API

HAProxy дозволяє виконувати миттєву зміну ваг і станів бекенд-серверів без перезавантаження процесу через локальний UNIX-сокет (`/var/run/haproxy.sock`). Це виключає накладні витрати на передачу файлових дескрипторів між майстер- і воркер-процесами, забезпечуючи час реакції менше 1 мілісекунди.

Керування здійснюється за допомогою простих текстових команд, що надсилаються в інтерактивному режимі або через утиліту `socat`.

### Матриця станів сервера в HAProxy

Кожен бекенд-сервер у пулі HAProxy може перебувати в одному з чотирьох взаємовиключних станів, які визначають правила обробки трафіку:

| Стан сервера | Доступність для нових з'єднань | Обробка існуючих відкритих TCP-сесій | Використання в синьо-зеленій схемі |
| :--- | :--- | :--- | :--- |
| `ready` | **Так** (повне балансування) | Повна обробка | Активне робоче середовище (100% трафіку). |
| `drain` | **Ні** (нові сесії блокуються) | Дозволяється завершити активні з'єднання | Фаза дренажу старого середовища після перемикання. |
| `maint` | **Ні** (повне відключення) | Усі сесії негайно розриваються | Режим очікування (Standby) або технічне обслуговування. |
| `down` | **Ні** (провал health-check) | Скидання з'єднань | Автоматично фіксується у разі збою вузла. |

### Послідовність команд перемикання та аварійного відкату

Процедура перемикання складається з послідовного переводу цільових серверів у робочий стан `ready`, встановлення повної ваги `weight 100` та переводу попередніх серверів у режим безпечного вичерпання з'єднань `drain`.

У разі виявлення критичної аномалії зворотна послідовність повертає синій пул у роботу за одну операцію, а зелені сервери переводяться в ізольований стан `maint` для збереження стану оперативної пам'яті та подальшого аналізу аварійних дампів.

При роботі з сесійною прив'язкою (Sticky Sessions на основі кук `appsession` або stick-tables) переведення вузлів у статус `drain` гарантує, що клієнти з уже існуючою сесійною кукою продовжать надсилати запити на свій старий сервер доти, доки їхня сесія не завершиться або не закінчиться ліміт часу дренажу. Усі нові клієнти без куки негайно балансуватимуться на сервери в стані `ready`.

```bash
# 1. Перевірка стану серверів у пулах
echo "show stat" | socat stdio /var/run/haproxy.sock | cut -d ',' -f 1,2,18,19

# 2. Активація зеленого середовища (переведення вузлів у статус ready)
echo "set server backend_green/srv_g1 state ready" | socat stdio /var/run/haproxy.sock
echo "set server backend_green/srv_g2 state ready" | socat stdio /var/run/haproxy.sock

# 3. Встановлення повної ваги для зеленого пулу
echo "set server backend_green/srv_g1 weight 100" | socat stdio /var/run/haproxy.sock
echo "set server backend_green/srv_g2 weight 100" | socat stdio /var/run/haproxy.sock

# 4. Переведення синього пулу в режим дренажу (нові запити не йдуть, старі добігають)
echo "set server backend_blue/srv_b1 state drain" | socat stdio /var/run/haproxy.sock
echo "set server backend_blue/srv_b2 state drain" | socat stdio /var/run/haproxy.sock

# 5. ЕКСТРЕНИЙ ВІДКАТ НА СИНІЙ (виконується за 1 мс у разі збою)
echo "set server backend_blue/srv_b1 state ready" | socat stdio /var/run/haproxy.sock
echo "set server backend_blue/srv_b2 state ready" | socat stdio /var/run/haproxy.sock
echo "set server backend_green/srv_g1 state maint" | socat stdio /var/run/haproxy.sock
echo "set server backend_green/srv_g2 state maint" | socat stdio /var/run/haproxy.sock
```

### Конфігурація `haproxy.cfg` з підтримкою сокета керування

Конфігурація визначає глобальний сокет адміністративного рівня та два незалежні бекенди `backend_blue` і `backend_green`, об'єднані в динамічний пул зваженого балансування `dynamic_app_pool`.

```haproxy
global
    stats socket /var/run/haproxy.sock mode 660 level admin expose-fd listeners
    stats timeout 30s

defaults
    mode http
    timeout connect 5000ms
    timeout client  50000ms
    timeout server  50000ms

frontend public_http_front
    bind *:80
    bind *:443 ssl crt /etc/ssl/certs/site.pem
    # Основний маршрут спрямовується на бекенд, керований динамічно через ваги
    default_backend dynamic_app_pool

backend dynamic_app_pool
    balance roundrobin
    option httpchk GET /healthz
    http-check expect status 200
    
    # Синій пул (початково активний)
    server srv_b1 10.0.1.11:8080 check weight 100
    server srv_b2 10.0.1.12:8080 check weight 100
    
    # Зелений пул (початково в режимі обслуговування)
    server srv_g1 10.0.2.21:8080 check weight 0 state maint
    server srv_g2 10.0.2.22:8080 check weight 0 state maint
```

---

## 4. Специфікація перемикання цільових груп у хмарі (AWS ALB Target Groups)

У середовищі Amazon Web Services розгортання реалізується за допомогою сервісу Application Load Balancer (ALB) та двох незалежних цільових груп (`TargetGroupBlue` та `TargetGroupGreen`).

Керування здійснюється через API-виклик `elasticloadbalancingv2:ModifyListener` або зміну ваг у правилах маршрутизації слухача (`Listener Rules`). Хмарний балансувальник надає апаратну ізоляцію відмов та підтримує безшовний перерозподіл тисяч паралельних з'єднань між цільовими групами.

### Таблиця атрибутів цільової групи (Target Group Attributes)

| Атрибут AWS ALB | Тип | Рекомендоване значення | Інженерне призначення |
| :--- | :--- | :--- | :--- |
| `deregistration_delay.timeout_seconds` | `integer` | `30`–`60` | Тривалість дренажу з'єднань. Визначає, скільки часу балансувальник очікує завершення активних запитів перед видаленням інстансу з пулу. |
| `slow_start.duration_seconds` | `integer` | `30` | Режим плавного старту. Дозволяє новому інстансу поступово нарощувати частку запитів, запобігаючи перевантаженню процесора під час JIT-компіляції. |
| `stickiness.enabled` | `boolean` | `true` (за потребою) | Вмикає генерацію куки `AWSALB` для сесійної прив'язки користувача до конкретної цільової групи. |

### Механізм Slow Start та поступового прогріву
Параметр `slow_start.duration_seconds` є критично важливим для важких веб-додатків на базі Java, .NET або Node.js. Коли новий інстанс реєструється в цільовій групі зеленого середовища та успішно проходить первинний health-check, балансувальник не спрямовує на нього повну частку запитів одразу. Протягом періоду Slow Start (наприклад, 30–60 секунд) інстанс отримує поступово зростаючий відсоток трафіку за лінійною функцією. Це дозволяє JIT-компілятору оптимізувати байткод, а пулу з'єднань із базою даних плавно відкрити сокети без ризику сплеску тайм-аутів.

Після закінчення періоду Slow Start інстанс автоматично переходить у режим повного зваженого балансування.

### Фрагмент маніфесту Terraform для атомарного перемикання ALB

Маніфест демонструє конфігурацію правила слухача, де 100% трафіку спрямовується на зелену цільову групу, тоді як синя цільова група залишається прив'язаною з нульовою вагою для швидкого аварійного відкату.

```hcl
resource "aws_lb_listener_rule" "production_traffic_rule" {
  listener_arn = aws_lb_listener.front_end_ssl.arn
  priority     = 100

  action {
    type = "forward"
    forward {
      target_group {
        arn    = aws_lb_target_group.green_pool.arn
        weight = 100
      }
      target_group {
        arn    = aws_lb_target_group.blue_pool.arn
        weight = 0
      }
      stickiness {
        enabled  = true
        duration = 3600
      }
    }
  }

  condition {
    path_pattern {
      values = ["/api/*"]
    }
  }
}
```

---

## 5. Контракт JSON-вебхука автоматизованої верифікації здоров'я

Зовнішні аналізатори розгортання та CI/CD конвеєри (Spinnaker, Argo CD, Jenkins X) використовують стандартизований HTTP/JSON вебхук для опитування зовнішніх тестових раннерів перед ухваленням рішення про перемикання трафіку.

Вебхук забезпечує повну ізоляцію логіки тестування від конфігурації інфраструктури: оркестратор лише передає ідентифікатор релізу, адресу прев'ю-ендпоінта та цільові пороги SLO, а спеціалізований сервіс тестування самостійно генерує навантаження, збирає відповіді та повертає машиночитний вердикт.

### Протокол взаємодії та обробка відмов
Взаємодія будується на основі моделі синхронного або асинхронного опитування (англ. *Polling*). Оркестратор надсилає HTTP-запит `POST` на адресу тестового вебхука. Сервіс верифікації виконує набір синтетичних сценаріїв або аналізує вікно метрик у Prometheus/Datadog за вказаний період `metricsWindowSeconds`.

Якщо сервіс верифікації не відповідає протягом заданого тайм-ауту (наприклад, 15 секунд), оркестратор застосовує політику повторних спроб із затримкою. Якщо вебхук повертає код помилки `5xx` або вердикт `FAIL`, конвеєр розгортання автоматично блокує перемикання трафіку та ініціює безпечне згортання цільового середовища.

### Алгебра розрахунку SLI у сервісі верифікації
Сервіс верифікації розраховує два ключові показники надійності:
1. **Частота помилок (Error Rate SLI):** частка відповідей зі статусами `500 Internal Server Error`, `502 Bad Gateway`, `503 Service Unavailable` та `504 Gateway Timeout` від загальної кількості надісланих запитів.
2. **Затримка відповіді 99-го перцентилю (Latency p99 SLI):** максимальний час, протягом якого обслуговується 99% найшвидших запитів. Цей показник відсікає випадкові аномалії поодиноких запитів, проте надійно виявляє деградацію системного відгуку через блокування бази даних або збирання сміття (GC pauses).

### JSON-схема запиту аналізатора (`POST /api/v1/deployment/verify`)

Запит формується оркестратором на етапі `PrePromotionAnalysis` і містить усі параметри, необхідні для запуску інтеграційних тестів. Схема визначає суворі обмеження на типи полів, діапазони значень та обов'язкові параметри надійності.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": [
    "deploymentId",
    "targetEnvironment",
    "targetVersion",
    "previewEndpoint",
    "metricsWindowSeconds",
    "sloThresholds"
  ],
  "properties": {
    "deploymentId": {
      "type": "string",
      "format": "uuid",
      "description": "Унікальний ідентифікатор запуску конвеєра розгортання."
    },
    "targetEnvironment": {
      "type": "string",
      "enum": ["blue", "green"],
      "description": "Контур, який підлягає верифікації."
    },
    "targetVersion": {
      "type": "string",
      "description": "Семантична версія або SHA коміту нового артефакту."
    },
    "previewEndpoint": {
      "type": "string",
      "format": "uri",
      "description": "URL прев'ю-сервісу для виконання тестових запитів."
    },
    "metricsWindowSeconds": {
      "type": "integer",
      "minimum": 10,
      "maximum": 3600,
      "description": "Тривалість вікна збору метрик для розрахунку SLI."
    },
    "sloThresholds": {
      "type": "object",
      "required": ["maxErrorRatePercent", "maxP99LatencyMs"],
      "properties": {
        "maxErrorRatePercent": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 100.0,
          "description": "Максимально допустимий відсоток помилок HTTP 5xx."
        },
        "maxP99LatencyMs": {
          "type": "number",
          "minimum": 1.0,
          "description": "Граничний час обробки 99-го перцентилю запитів у мілісекундах."
        }
      }
    }
  }
}
```

### JSON-схема відповіді верифікатора (`200 OK`)

Відповідь верифікатора містить однозначний результат перевірки (`PASS`, `FAIL` або `INCONCLUSIVE`), числовий звіт про фактично зафіксовані показники та текстовий опис знайдених дефектів у разі провалу тестів.

У разі повернення статусу `FAIL` оркестратор негайно зупиняє розгортання, фіксує аварійний лог у системі аудиту та ініціює оповіщення чергових інженерів через систему чергування (PagerDuty або Opsgenie). Статус `INCONCLUSIVE` сигналізує про нестачу даних телеметрії (наприклад, недостатня кількість зразків запитів) і спонукає контролер повторити опитування через додатковий часовий інтервал.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": [
    "verdict",
    "evaluatedAt",
    "metrics",
    "reason"
  ],
  "properties": {
    "verdict": {
      "type": "string",
      "enum": ["PASS", "FAIL", "INCONCLUSIVE"],
      "description": "Остаточний вердикт: PASS дозволяє перемикання, FAIL ініціює відкат."
    },
    "evaluatedAt": {
      "type": "string",
      "format": "date-time",
      "description": "Мітка часу формування звіту за стандартом ISO 8601."
    },
    "metrics": {
      "type": "object",
      "required": ["observedErrorRatePercent", "observedP99LatencyMs", "totalSampledRequests"],
      "properties": {
        "observedErrorRatePercent": { "type": "number" },
        "observedP99LatencyMs": { "type": "number" },
        "totalSampledRequests": { "type": "integer" }
      }
    },
    "reason": {
      "type": "string",
      "description": "Людськочитне обґрунтування вердикту з переліком аномалій."
    }
  }
}
```

### Безпека та контроль доступу до адміністративних інтерфейсів
Усі описані вище протоколи динамічного керування (UNIX-сокет HAProxy, адміністративний порт Envoy 19000, API контролера Argo Rollouts) надають необмежений доступ до маршрутизації виробничого трафіку. Для захисту від несанкціонованого втручання застосовуються наступні інваріанти безпеки:
1. **Права доступу до сокета:** UNIX-доменний сокет HAProxy створюється з правами `0660` і належить системній групі `haproxy-admin`. Будь-який доступ неавторизованих процесів блокується на рівні ядра Linux.
2. **Ізоляція xDS:** зв'язок між Envoy та сервером керування захищається взаємною TLS-автентифікацією (mTLS) із перевіркою SAN сертифікатів.
3. **RBAC у Kubernetes:** доступ до ресурсів `Rollout` та `AnalysisRun` обмежується виключно системними сервісними акаунтами CI/CD конвеєра через механізм ролей `ClusterRole`.

