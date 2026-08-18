# 📋 Контракт внутрішньої платформи self-service Digital Homes

Цей документ визначає точний міжкомандний інтерфейсний контракт («Golden Path Platform Contract») між Платформною командою (Platform Team) та командами потоку цінності (Stream-aligned Teams) у системі Digital Homes. Інтерфейс є виключно програмованим і складається з Self-Service API, командного інструментарію CLI, набору програмних бібліотек (SDK) та декларативних маніфестів ресурсів. Його головна мета — повністю усунути будь-які людські черги, міжкомандні тікети в Jira та синхронні узгодження при створенні, масштабуванні, конфігуруванні й оновленні інфраструктурних ресурсів. 

Платформа функціонує в суворому режимі **X-as-a-Service**: розробник Stream-команди описує необхідний інфраструктурний вузол у декларативному маніфесті, а платформний контролер гарантує його автоматичне створення, мережеве ізолювання, моніторинг, резервне копіювання та відновлення без участі системних адміністраторів.

---

## 1. Архітектура та фундаментальні принципи Golden Path

Платформна інженерія в Digital Homes спирається на три непорушні соціотехнічні принципи:

1. **Самообслуговування без людського втручання (Zero-Touch Provisioning):** жоден крок створення бази даних PostgreSQL, кластера брокерів MQTT, таблиці TimescaleDB чи TLS-сертифіката не вимагає очікування чи людського схвалення адміна. Якщо команда має достатню квоту в доменному просторі, ресурс розгортається автоматично за програмованим викликом за 2–3 хвилини.
2. **Безпечні й стійкі дефолти (Secure by Default):** ресурс, замовлений через платформу, відразу дістає увімкнене шифрування даних під час зберігання та передачі (LUKS, TLS 1.3, KMS), авторотацію паролів через HashiCorp Vault, мережеву ізоляцію на рівні Kubernetes NetworkPolicies, автоматичний експорт метрик у Prometheus та щоденне резервне копіювання з перевіркою відновлення.
3. **Еволабельність та відсутність мандата:** Платформа не є бюрократичною диктатурою. Stream-команда має право побудувати власний інфраструктурний вузол руками, якщо має обґрунтовану потребу, але в такому разі вона повністю позбавляється підтримки платформного SLA й зобов'язана самостійно здійснювати цілодобову on-call підтримку цього вузла.

---

## 2. Специфікація декларативних маніфестів та каталогу ресурсів

Кожен сервіс та інфраструктурний ресурс, що створюється Stream-командою, реєструється в єдиному платформному каталозі (Developer Portal) через декларативні маніфести `catalog-info.yaml` та розширення Kubernetes Custom Resource Definitions (CRD).

### 2.1. Механізм та поля опису компонента платформи (Component Entity)

Специфікація компонента описує суворе володіння сервісом, міжсервісні залежності, прив'язані моніторингові дашборди Grafana та правила сповіщень у PagerDuty.

Маніфест обов'язково містить такі поля:
- `metadata.name`: унікальне ім'я сервісу в реєстрі платформи.
- `metadata.annotations.digitalhomes.io/team-owner`: ідентифікатор команди-власника, на яку адресуються сповіщення про аварії.
- `metadata.annotations.digitalhomes.io/pagerduty-service`: ключ сервісу в PagerDuty для ротації on-call інженерів.
- `spec.providesApis`: перелік публічних контракту API (gRPC, REST, AsyncAPI), які надає цей сервіс іншим командам.
- `spec.consumesApis`: перелік зовнішніх API, від яких залежить працездатність цього компонента.

```yaml
# catalog-info.yaml — Обов'язкова специфікація реєстрації сервісу
apiVersion: platform.digitalhomes.io/v1alpha1
kind: Component
metadata:
  name: device-twin-service
  namespace: smart-home-core
  description: "Сервіс цифрового двійника пристроїв та маршрутизації команд керування"
  labels:
    domain: "control"
    tier: "critical-path"
  annotations:
    digitalhomes.io/team-owner: "team-twin-control"
    digitalhomes.io/slack-channel: "#team-twin-dev"
    digitalhomes.io/pagerduty-service: "P38X1A"
    digitalhomes.io/grafana-dashboard: "https://grafana.dh.internal/d/twin-control-main"
spec:
  type: service
  lifecycle: production
  owner: team-twin-control
  system: smart-home-platform
  providesApis:
    - device-twin-grpc-v1
  consumesApis:
    - platform-mqtt-ingest-v2
  dependsOnResources:
    - resource:smart-home-core/device-twin-postgres-db
    - resource:smart-home-core/telemetry-timescale-buffer
```

### 2.2. Механізм замовлення сховища даних (PostgreSQL Resource CRD)

Stream-команда замовляє базу даних декларативним маніфестом, який зчитується платформовим контролером (Platform Operator), що жене реальні виклики до AWS RDS чи Kubernetes Operator.

Контролер перевіряє такі інваріанти:
- Обсяг запитаного дискового простору не перевищує ліміт квоти команди.
- Усі назви баз даних та секретів відповідають корпоративному стандарту найменування.
- Режим високої доступності (Multi-AZ) обов'язково увімкнений для середовища `production`.

```yaml
# postgres-resource.yaml — Замовлення бази даних для цифрового двійника
apiVersion: platform.digitalhomes.io/v1alpha1
kind: PostgresDatabase
metadata:
  name: device-twin-postgres-db
  namespace: smart-home-core
spec:
  teamOwner: "team-twin-control"
  serviceRef: "device-twin-service"
  engineVersion: "16.2"
  storage:
    allocatedGb: 300
    autoScalingGbMax: 1000
    storageClass: "gp3-nvme-high-iops"
  highAvailability:
    enabled: true
    multiAz: true
    readReplicas: 2
  backup:
    scheduleCron: "0 */2 * * *"
    retentionDays: 30
    pitrEnabled: true
  security:
    sslMode: "verify-full"
    vaultSecretEnginePath: "secret/data/smart-home-core/twin-db"
    allowedSubnets:
      - "10.240.12.0/24"
      - "10.240.13.0/24"
```

---

## 3. Програмований API-контракт та асинхронний цикл provisioning

Платформа надає REST та gRPC API для інструментів CI/CD, Terraform-провайдера та внутрішніх CLI. Створення інфраструктурного ресурсу є **ідемпотентною асинхронною операцією**, оскільки розгортання сховища чи брокера в хмарі займає від декількох секунд до 3 хвилин.

### 3.1. Послідовність викликів та фази розгортання

1. **Запит Stream-команди:** `POST /v1/resources/postgresql` з унікальним ключем ідемпотентності `X-Idempotency-Key` у заголовку. Ключ унеможливлює подвійне створення бази при мережевих ретраях.
2. **Відповідь платформи:** статус `202 Accepted` з унікальним ідентифікатором завдання `jobId` та посиланням на опитач стану `GET /v1/jobs/{jobId}`.
3. **Виконання платформного контролера:**
   - Валідація квоти команди та перевірка безпекових лімітів мережі.
   - Виклики Terraform / Crossplane контролерів для підняття ресурсів в хмарі.
   - Генерація динамічних облікових записів та ключів у HashiCorp Vault.
   - Створення Grafana-дашборда й Alertmanager-правил для даного ресурсу.
4. **Завершення:** статус операції переходить у `COMPLETED`, повертаючи посилання на Kubernetes Secret з доступами.

### 3.2. Ідіоматичні реалізації SDK самообслуговування

Нижче наведено робочий код клієнтської бібліотеки платформи двома мовами розробки, що реалізує асинхронне замовлення з обробкою таймаутів, повторів та ідемпотентності.

:::tabs
```py
# platform_client.py — Робочий Python SDK платформи для Stream-команд
import time
import uuid
import logging
import requests
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DHPlatformClient")

@dataclass
class DatabaseProvisionSpec:
    service_name: str
    team_id: str
    db_name: str
    allocated_storage_gb: int
    enable_ha: bool = True
    backup_retention_days: int = 30

class DHPlatformException(Exception):
    """Базовий виняток при помилці платформи."""
    pass

class DigitalHomesPlatformClient:
    """
    Платформний клієнт для замовлення інфраструктури без квитанцій і чекання.
    """
    def __init__(self, endpoint: str, api_token: str, timeout_sec: float = 15.0):
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout_sec
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "X-DH-Client-Version": "2.4.0-py"
        })

    def provision_postgres_database(
        self, 
        spec: DatabaseProvisionSpec, 
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ідемпотентний запит на створення бази даних.
        """
        if not idempotency_key:
            idempotency_key = str(uuid.uuid4())

        url = f"{self.endpoint}/v1/resources/postgresql"
        headers = {"X-Idempotency-Key": idempotency_key}
        payload = asdict(spec)

        logger.info("Надсилання запиту на розгортання БД '%s' для команди '%s'", spec.db_name, spec.team_id)
        
        try:
            resp = self.session.post(url, json=payload, headers=headers, timeout=self.timeout)
        except requests.RequestException as e:
            raise DHPlatformException(f"Мережева помилка зв'язку з платформою: {e}") from e

        if resp.status_code != 202:
            raise DHPlatformException(f"Платформа відхилила запит ({resp.status_code}): {resp.text}")

        job_data = resp.json()
        job_id = job_data.get("jobId")
        logger.info("Запит прийнято платформою. JobID: %s. Починаємо опитування...", job_id)
        
        return self._poll_job_until_completion(job_id)

    def _poll_job_until_completion(self, job_id: str, max_wait_sec: int = 180) -> Dict[str, Any]:
        url = f"{self.endpoint}/v1/jobs/{job_id}"
        start_time = time.time()

        while time.time() - start_time < max_wait_sec:
            try:
                resp = self.session.get(url, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    status = data.get("status")
                    
                    if status == "COMPLETED":
                        logger.info("Ресурс успішно розгорнуто платформою за %.1f сек!", time.time() - start_time)
                        return data.get("resultResource", {})
                    elif status == "FAILED":
                        error_msg = data.get("error", "Невідома помилка платформи")
                        raise DHPlatformException(f"Створення ресурсу провалилося: {error_msg}")
                    
                    logger.debug("Стан розгортання [%s]... Чекаємо 4 сек.", status)
            except requests.RequestException as e:
                logger.warning("Тимчасова помилка опитача: %s. Повторюємо...", e)

            time.sleep(4.0)

        raise DHPlatformException(f"Перевищено таймаут очікування розгортання ресурсу ({max_wait_sec} сек)")
```
```ts
// platform-client.ts — Робочий TypeScript SDK платформи для Stream-команд
import { v4 as uuidv4 } from 'uuid';

export interface DatabaseProvisionSpec {
  serviceName: string;
  teamId: string;
  dbName: string;
  allocatedStorageGb: number;
  enableHa?: boolean;
  backupRetentionDays?: number;
}

export interface ResourceResult {
  resourceId: string;
  connectionSecretRef: string;
  status: 'READY' | 'FAILED';
  allocatedEndpoints: string[];
}

export class DHPlatformException extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'DHPlatformException';
  }
}

export class DigitalHomesPlatformClient {
  private readonly endpoint: string;
  private readonly apiToken: string;

  constructor(endpoint: string, apiToken: string) {
    this.endpoint = endpoint.replace(/\/+$/, '');
    this.apiToken = apiToken;
  }

  async provisionPostgresDatabase(
    spec: DatabaseProvisionSpec,
    idempotencyKey?: string
  ): Promise<ResourceResult> {
    const key = idempotencyKey || uuidv4();
    const url = `${this.endpoint}/v1/resources/postgresql`;

    console.log(`[PlatformClient] Запит БД '${spec.dbName}' для команди '${spec.teamId}'...`);

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiToken}`,
        'Content-Type': 'application/json',
        'X-Idempotency-Key': key,
        'X-DH-Client-Version': '2.4.0-ts',
      },
      body: JSON.stringify({
        serviceName: spec.serviceName,
        teamId: spec.teamId,
        dbName: spec.dbName,
        allocatedStorageGb: spec.allocatedStorageGb,
        enableHa: spec.enableHa ?? true,
        backupRetentionDays: spec.backupRetentionDays ?? 30,
      }),
    });

    if (response.status !== 202) {
      const errText = await response.text();
      throw new DHPlatformException(`Платформа відхилила запит (${response.status}): ${errText}`);
    }

    const { jobId } = await response.json() as { jobId: string };
    console.log(`[PlatformClient] Запит прийнято. JobID: ${jobId}. Опитування стану...`);

    return this.pollJobCompletion(jobId);
  }

  private async pollJobCompletion(jobId: string, maxWaitMs: number = 180000): Promise<ResourceResult> {
    const startTime = Date.now();
    const pollUrl = `${this.endpoint}/v1/jobs/${jobId}`;

    while (Date.now() - startTime < maxWaitMs) {
      try {
        const res = await fetch(pollUrl, {
          headers: { 'Authorization': `Bearer ${this.apiToken}` },
        });

        if (res.ok) {
          const data = await res.json() as { status: string; resultResource?: ResourceResult; error?: string };
          if (data.status === 'COMPLETED' && data.resultResource) {
            console.log(`[PlatformClient] Ресурс готовий за ${(Date.now() - startTime) / 1000}s!`);
            return data.resultResource;
          }
          if (data.status === 'FAILED') {
            throw new DHPlatformException(`Створення ресурсу завершилося помилкою: ${data.error}`);
          }
        }
      } catch (err) {
        if (err instanceof DHPlatformException) throw err;
        console.warn(`[PlatformClient] Тимчасовий збій мережі під час опитування: ${err}`);
      }

      await new Promise((r) => setTimeout(r, 4000));
    }

    throw new DHPlatformException(`Перевищено час очікування платформи (${maxWaitMs / 1000}s)`);
  }
}
```
:::

---

## 4. Опрацювання крайових випадків та нештатних ситуацій

Платформний контракт чітко обумовлює поведінку системи при виникненні аномалій та крайових випадків:

1. **Перевищення квот ресурсу (Quota Exhaustion):**
   Якщо Stream-команда вичерпала свій ліміт дискового простору чи CPU-ядер у кластері, платформа відразу повертає HTTP-статус `422 Unprocessable Entity` з детальним кодом помилки `QUOTA_EXCEEDED` та структурованим описом. Людям-адмінам тікети не надсилаються; збільшення квоти домену виконується автоматичним схваленням техліда домену у платформній консолі.
2. **Збій провайдера інфраструктури (Cloud Provider Failure):**
   Якщо хмарний провайдер (AWS чи GCP) повертає помилку нестачі ресурсів у конкретній зоні (Out of Capacity), платформний оператор обробляє це локально: автоматично перемикається на резервну зону доступності (Multi-AZ Failover) та виконує до 3 повторних спроб без видачі помилки на рівень Stream-команди.
3. **Ротація секретів та аварійний доступ (Secret Rotation & Break-Glass):**
   Усі доступи й паролі зберігаються в HashiCorp Vault. Stream-команда отримує лише посилання на Secret у Kubernetes (`secretRef`). Якщо стається аварія мережі і Vault тимчасово недоступний, платформний оператор підтримує закешований локальний секрет у розшифрованій пам'яті вузла протягом 24 годин.
4. **Конфлікти версій специфікацій (Schema Evolution):**
   Платформа підтримує одночасне існування двох суміжних версій API (наприклад, `v1alpha1` та `v1beta1`). При депрекації старої версії платформний інспектор автоматично надсилає PR-попередження в репозиторій Stream-команди за 30 днів до зняття підтримки.

---

## 5. Гарантії сервісного рівня та метрики стійкості (SLA / SLO / SLI)

Оскільки Платформна команда працює в режимі **X-as-a-Service**, вона бере на себе офіційні зобов'язання перед Stream-командами, які фіксуються в інтернальних угодах сервісного рівня.

### 5.1. Математична формалізація доступності платформи

Показник доступності платформного API розраховується за місячним інтервалом оцінки:

```
SLI_availability = (N_successful_api_calls / N_total_api_calls) · 100%
```

Де `N_successful_api_calls` — кількість запитів до Self-Service API, що повернули статуси 2xx або 202 протягом 30 календарних днів.

### 5.2. Таблиця гарантій сервісного рівня платформи

| Область | Індикатор (SLI) | Цільовий SLO | Дія при порушенні SLO |
| :--- | :--- | :--- | :--- |
| **Доступність Self-Service API** | Успішність викликів API розгортання | **≥ 99.9%** на місяць | Платформна команда зупиняє розробку нових фіч і лагодить контролер |
| **Швидкість розгортання БД** | Час від `POST` до стану `READY` | **< 180 сек** (p95) | Автоматична ескаляція на платформного архітектора |
| **Точність відновлення (RPO)** | Точка втрати даних при аварії | **< 60 секунд** (PITR) | Автоматичний запуск перевірочного проходу відновлення з бекапу |
| **Максимальний час відновлення (RTO)** | Час підняття інфраструктури з нуля | **< 30 хвилин** | Проведення міжкомандного Post-Mortem воркшопу |
| **Реакція на блокуючий інцидент** | Час відповіді на платформову аварію | **< 15 хвилин** (24/7) | Виклик чергового платформного інженера через PagerDuty |

Впровадження цього контракту дозволило Digital Homes повністю позбутися міжкомандного тренія та перетворити інфраструктуру на прозорий, швидкий і передбачуваний сервісний продукт.
