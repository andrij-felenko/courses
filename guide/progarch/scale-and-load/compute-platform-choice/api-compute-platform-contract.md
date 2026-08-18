# 📋 Декларативні специфікації та контракти розгортання compute-платформ

Контракт між обчислювальною платформою та застосунком декларує правила виділення ресурсів (CPU, RAM), межі ізоляції, стратегії автомасштабування та сигнали управління життєвим циклом процесу. Нижче наведено детальний розбір декларативних специфікацій для трьох основних моделей виконання: Kubernetes Manifests, AWS Fargate Task Definitions та systemd Service Units.

## 1. Специфікація контракту Kubernetes (k8s Manifests)

У кластерному середовищі Kubernetes контракт розгортання описується трьома базовими об'єктами: `Deployment` (декларація процесів), `HorizontalPodAutoscaler` (стратегія еластичного масштабування) та `ResourceQuota` (захист Multi-Tenant середовища).

### Механіка ресурсних обмежень (requests vs limits)

Поля `resources.requests` та `resources.limits` визначають рівень обчислювальної гарантії та клас якості обслуговування (QoS Class):

- **Guaranteed QoS (`requests == limits`):** Под отримує зарезервоване ядро та оперативну пам'ять, які не можуть бути вилучені іншими процесами на ноді. Планувальник (kube-scheduler) гарантує розташування поду лише на нодах із вільним обсягом ресурсів.
- **Burstable QoS (`requests < limits`):** Под гарантовано отримує обсяг `requests`, але може тимчасово забирати вільні процесорні такти хоста аж до межі `limits`. Перевищення межі CPU призводить до тротлінгу (CFS Throttling), а перевищення RAM — до виклику `OOMKiller`.
- **BestEffort QoS (відсутні `requests` та `limits`):** Под не надає жодних гарантій і є першим кандидатом на знищення при дефіциті оперативної пам'яті на ноді.

Конфігурація `readinessProbe` регулює момент включення поду в балансир навантаження (Service Endpoint), а `livenessProbe` контролює самовідновлення при зависанні внутрішніх потоків. 

Розділ `securityContext` декларує жорсткі межі безпеки виконання: прапорець `readOnlyRootFilesystem: true` блокує запис у контейнерний шар OverlayFS, змушуючи застосунок використовувати ефемерні томи `emptyDir` для тимчасових файлів, а `allowPrivilegeEscalation: false` запобігає отриманню прав root через SUID-бінарники.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dh-api-gateway
  namespace: prod-scale
spec:
  replicas: 10
  selector:
    matchLabels:
      app: dh-api-gateway
  template:
    metadata:
      labels:
        app: dh-api-gateway
    spec:
      containers:
      - name: gateway
        image: registry.digitalhomes.io/dh-api:v2.4.1
        resources:
          requests:
            cpu: "500m"        # 0.5 vCPU гарантовано під под
            memory: "512Mi"    # 512 MB RAM гарантовано
          limits:
            cpu: "2000m"       # 2.0 vCPU верхній поріг (cgroup throttling)
            memory: "1024Mi"   # 1.0 GB RAM верхній поріг (OOMKill при перевищенні)
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 3
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 15
          periodSeconds: 10
        securityContext:
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          runAsUser: 10001
          capabilities:
            drop:
            - ALL
```

### Декларація еластичного автомасштабування (HorizontalPodAutoscaler v2)

Об'єкт `HorizontalPodAutoscaler` періодично опитує `metrics-server` (за замовчуванням кожні 15 секунд) та розраховує необхідну кількість реплік за формулою `DesiredReplicas = ⌈ CurrentReplicas · ( CurrentMetricValue / TargetMetricValue ) ⌉`.

Політика масштабування у розділі `behavior` розрізняє реакцію на зростання трафіку (`scaleUp`) та згортання (`scaleDown`). Застосування параметра `stabilizationWindowSeconds: 300` для згортання запобігає каскадному дефіциту ресурсів при повторних сплесках навантаження.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: dh-api-gateway-hpa
  namespace: prod-scale
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: dh-api-gateway
  minReplicas: 10
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

## 2. Специфікація контракту Serverless / Fargate (AWS Task Definition)

У безсерверній модель AWS ECS/Fargate контракт описується через файл специфікації ECS Task Definition. На відміну від довільного вибору ресурсів у Kubernetes, Fargate вимагає вибору суворих дискретних пар CPU та RAM із сітки провайдера (наприклад, 256 CPU units / 512 MB RAM, 512 CPU units / 1024 MB RAM, 1024 CPU units / 2048 MB RAM до 16 vCPU / 120 GB RAM).

Контракт Fargate ізолює процес у власному мережевому стеку `awsvpc`, виділяючи окрему віртуальну мережеву карту (ENI) із власною приватною IP-адресою у VPC. Це повністю позбавляє контейнери проблеми конфлікту портів на хості, але вимагає додаткових 10–15 секунд на виділення ENI під час холодного старту.

Розділ `logConfiguration` визначає стримінг логів безпосередньо у хмарний сервіс AWS CloudWatch через драйвер `awslogs`, виключаючи локальне накопичення логів на ефемерному диску.

Опція `ephemeralStorage` дозволяє збільшити розмір тимчасового диска від дефолтних 20 GB до 200 GB для обробки великих файлів. Параметр `stopTimeout` декларує час (за замовчуванням 30 секунд), який надається контейнеру після надсилання сигналу `SIGTERM` для завершення активних з'єднань перед примусовим надсиланням `SIGKILL`.

```json
{
  "family": "dh-event-webhook-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": [
    "FARGATE"
  ],
  "cpu": "512",
  "memory": "1024",
  "ephemeralStorage": {
    "sizeInGiB": 30
  },
  "containerDefinitions": [
    {
      "name": "webhook-worker",
      "image": "registry.digitalhomes.io/dh-webhook:v1.2.0",
      "essential": true,
      "stopTimeout": 30,
      "portMappings": [
        {
          "containerPort": 8080,
          "hostPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/dh-event-webhook",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "fargate"
        }
      },
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8080/health || exit 1"
        ],
        "interval": 10,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 15
      }
    }
  ]
}
```

## 3. Специфікація контракту Bare Metal / Direct VM (systemd Service Unit)

При прямому розгортанні на фізичний сервер або IaaS віртуальну машину контракт між ядром ОС Linux та застосунком декларується через файл служби systemd з використанням підсистеми `cgroups v2`.

### Параметри низькорівневої ізоляції та тротлінгу

- `CPUQuota=400%`: Обмежує споживання процесорного часу еквівалентом 4 повних ядер CPU. Перевищення ліміту призводить до тротлінгу через плагін `CFS scheduler`.
- `CPUAffinity=0 1 2 3`: Жорстко прив'язує процес до фізичних ядер 0, 1, 2 та 3. Це повністю виключає міжпроцесорне перемикання контексту та підвищує влучання в L1/L2 кеш CPU.
- `MemoryHigh=3500M` та `MemoryMax=4000M`: `MemoryHigh` вмикає фонове вимивання сторінок (Reclaim) при досягненні 3.5 GB, а `MemoryMax` є жорстким порогом, при перевищенні якого ядро надсилає сигнал `SIGKILL` через підсистему OOM.
- `MemorySwapMax=0`: Категорично забороняє вивантаження пам'яті сервісу в файл підкачки (Swap), що запобігає непередбачуваним затримкам дискового I/O при дефіциті RAM.
- `LimitNOFILE=1048576`: Збільшує ліміт відкритих файлових дескрипторів із дефолтних 1024 до 1 мільйона, що необхідно для утримання сотень тисяч TCP-сокетів.
- `OOMScoreAdjust=-500`: Знижує ймовірність знищення ядра у разі загального дефіциту оперативної пам'яті в системі, надаючи перевагу збереженню вхідного gRPC-шлюзу.
- `ProtectSystem=strict` та `CapabilityBoundingSet`: Забезпечують жорсткий санбоксинг, забороняючи процесу модифікувати системні директорії `/usr`, `/boot` та залишаючи лише мінімальний набір системних прав ядра Linux (`CAP_NET_BIND_SERVICE`).

```ini
[Unit]
Description=Digital Homes IoT Ingest Service (Stateful gRPC Stream)
After=network.target remote-fs.target
Wants=network-online.target

[Service]
Type=notify
User=dh-ingest
Group=dh-ingest
WorkingDirectory=/opt/dh/ingest
ExecStart=/opt/dh/ingest/bin/dh-ingest-service --config=/etc/dh/ingest.conf
ExecReload=/bin/kill -HUP $MAINPID

# 1. Ресурсні обмеження cgroups v2
CPUAccounting=true
CPUQuota=400%
CPUAffinity=0 1 2 3
MemoryAccounting=true
MemoryHigh=3500M
MemoryMax=4000M
MemorySwapMax=0
OOMScoreAdjust=-500

# 2. Мережеві та файлові ліміти
LimitNOFILE=1048576
LimitNPROC=65536
TasksMax=16384

# 3. Стратегія перезапуску та сигналів
Restart=always
RestartSec=3s
TimeoutStopSec=30s
KillSignal=SIGTERM
SuccessExitStatus=143
KillMode=mixed

# 4. Безпека та санбоксінг ядра
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
CapabilityBoundingSet=CAP_NET_BIND_SERVICE CAP_NET_RAW

[Install]
WantedBy=multi-user.target
```

## 4. Спостережуваність та телеметрія контрактів (Observability)

Контракти розгортання суттєво відрізняються способом збору метрик продуктивності та логів:

1. **Kubernetes Observability:** Збір метрик реалізується через Prometheus Operator, який опитує `kubelet` та `/metrics` ендпоінти подів. Метрики cgroups витягуються через `cadvisor` (поля `container_cpu_usage_seconds_total`, `container_memory_working_set_bytes`). Логи збираються DaemonSet-агентами (Fluentbit, Vector) із директорії `/var/log/pods`.
2. **AWS Fargate Observability:** Відсутність доступу до хоста змушує використовувати AWS CloudWatch Container Insights або боковий контейнер (Sidecar) AWS Firelens (на базі Fluent Bit), який перехоплює stdout/stderr та відправляє у Datadog, Grafana Loki чи Elasticsearch.
3. **Bare Metal Observability:** Використовує прямі експортери ядра (Node Exporter, eBPF `bcc`/`bpftrace` скрипти). Демон `systemd-cgtop` дає миттєву картину використання ресурсів за cgroup-слайсами, а `journalctl -u dh-ingest.service` забезпечує низьколатентний доступ до логів без проміжних агентів.

## 5. Зведена порівняльна таблиця характеристик контрактів

У таблиці нижче підсумовано ключові відмінності в керуванні ресурсами, мережевій ізоляції та сигналах життєвого циклу процесів.

| Параметр контракту | Kubernetes (K8s Manifest) | AWS Fargate / Serverless | Bare Metal / systemd |
| :--- | :--- | :--- | :--- |
| **Одиниця виділення CPU** | Міліядра (`1000m` = 1 vCPU) | Фіксовані юніти (256, 512, 1024, 2048) | Відсоток CPUQuota (`400%` = 4 ядра) або CPUAffinity |
| **Реакція на перевищення RAM** | `OOMKilled` статус поду | Завершення та перезапуск ECS Task | `MemoryMax` виклики OOM Killer ядра Linux |
| **Режим ізоляції мережі** | CNI (Calico, Cilium, Overlay IP) | `awsvpc` (власний Elastic Network Interface) | Host Networking / Direct Physical Interface |
| **Час реакції на Scaling Event** | 10–30 секунд (HPA query + Pod Schedule) | 15–45 секунд (Provisioning Fargate VM) | Хвилини/Години (Provisioning IaaS VM / Metal) |
| **Контроль ядерок (CPU Pinning)** | `Kubelet static policy` (потрібен Guaranteed QoS) | Відсутній (визначається провайдером) | Повний (`CPUAffinity=0,1,2,3`, `numactl`) |
| **Отримання метрик (Observability)** | Prometheus Operator / Metrics Server | AWS CloudWatch Container Insights | systemd-cgtop / eBPF exporters / Node Exporter |
