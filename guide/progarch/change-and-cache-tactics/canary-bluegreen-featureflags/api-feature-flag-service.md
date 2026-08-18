# 📋 Специфікація та контракт API Feature Flag Engine

Ця довідкова вставка визначає специфікацію публічного інтерфейсу (API) та схеми даних сервісу управління прапорцями функцій (Feature Flag Engine). Вона встановлює контракт між сервером конфігурацій прапорців, клієнтськими SDK та конвеєром автоматичного канарейкового деплою.

## 1. Контракт локального SDK (In-Memory Evaluation Interface)

Для досягнення високої швидкодії з латентністю обчислення `< 1 µs` оцінка прапорців виконується повністю у пам'яті процесів застосунку. Клієнтський SDK реалізує строгий типізований інтерфейс, який ізолює бізнес-код від мережевих збоїв та внутрішніх змін структури правил.

### Анатомія контексту оцінки (Evaluation Context)

Контекст оцінки є об'єктом, що збирає атрибути поточного суб'єкта виклику (користувача, домашнього хаба, запиту). Контекст не повинен містити чутливих секретів (паролів, приватних ключів), оскільки його атрибути беруть участь у розрахунку статистичних бакетів та надсилаються у буфер телеметрії.

```ts
interface EvaluationContext {
  userId: string;
  tenantId: string;
  userRole: string;
  country?: string;
  appVersion?: string;
  attributes?: Record<string, string | number | boolean>;
}
```

### Сигнатури методів SDK та типи варіацій

SDK надає розширені методи для отримання примітивних типів та складних об'єктів конфігурації. Метод `evaluateDetail` повертає звіт про причинно-наслідковий зв'язок оцінки, що є необхідним для відлагодження політик та реєстрації аудит-логів.

```ts
interface FeatureFlagSDK {
  // Оцінка булевого прапорця
  boolVariation(
    flagKey: string, 
    context: EvaluationContext, 
    defaultValue: boolean
  ): boolean;

  // Оцінка мультиваріантного прапорця (строкові конфігурації)
  stringVariation(
    flagKey: string, 
    context: EvaluationContext, 
    defaultValue: string
  ): string;

  // Оцінка складної JSON-конфігурації для динамічного налаштування
  jsonVariation<T>(
    flagKey: string, 
    context: EvaluationContext, 
    defaultValue: T
  ): T;

  // Оцінка з поверненням детального причинно-наслідкового звіту
  evaluateDetail<T>(
    flagKey: string, 
    context: EvaluationContext, 
    defaultValue: T
  ): EvaluationDetail<T>;
}

interface EvaluationDetail<T> {
  value: T;
  variationIndex?: number;
  reason: "OFF_FALLBACK" | "TARGET_MATCH" | "PERCENTAGE_ROLLOUT" | "RULE_MATCH" | "DEFAULT";
  ruleId?: string;
}
```

Поле `reason` приймає наступні значення:
- `OFF_FALLBACK`: прапорець вимкнено на центральному сервері, повернуто значення за замовчуванням.
- `TARGET_MATCH`: користувач прямо вказаний у списку дозволених ID (`targetUsers`).
- `PERCENTAGE_ROLLOUT`: рішення прийнято на основі детермінованого розрахунку бакета хешування відсотка викатки.
- `RULE_MATCH`: спрацювало одне з додаткових правил атрибутів (наприклад, збіг за рольовим правилом чи геозоною).
- `DEFAULT`: прапорець відсутній у наборі правил, задіяно дефолтне значення з коду.

---

## 2. HTTP REST API: Отримання конфігурації прапорців SDK (Sync Pipeline)

Сервіси застосунку періодично опитують central flag server для оновлення локального знімка правил у пам'яті. Механізм спирається на заголовки HTTP Caching (`ETag` та `If-None-Match`) для мінімізації трафіку та навантаження на мережу.

### GET `/api/v1/flags/ruleset`

Повертає повний знімок (Ruleset Snapshot) активних прапорців для поточного оточення.

**Запити (Headers):**
- `Authorization: Bearer <SDK_ENVIRONMENT_KEY>`
- `If-None-Match: "<ETAG_VALUE>"` (підтримка HTTP 304 Not Modified)

**Опис полів відповіді:**
- `version`: монотонно зростаючий лічильник версії конфігурації.
- `updatedAt`: ISO-8601 штамп останнього редагування наборів правил.
- `salt`: унікальна сіль прапорця, що запобігає кореляції викатки між різними функціями.
- `fallthrough`: дефолтне правило, яке застосовується, якщо жодне з цільових таргетингових правил не спрацювало.

**Успішна відповідь `200 OK` (JSON):**

```json
{
  "version": 4028,
  "updatedAt": "2026-08-18T09:00:00Z",
  "flags": {
    "smart_lock_v2_algorithm": {
      "key": "smart_lock_v2_algorithm",
      "state": "PERCENTAGE_ROLLOUT",
      "version": 3,
      "rolloutPercentage": 10,
      "salt": "salt_lock_v2_x89",
      "targetUsers": ["user_beta_01", "user_beta_02"],
      "targetRoles": ["beta_tester", "admin"],
      "rules": [
        {
          "id": "rule_internal_devs",
          "attribute": "tenantId",
          "operator": "IN",
          "values": ["dh_internal_office"],
          "variation": true
        }
      ],
      "fallthrough": {
        "rolloutPercentage": 10
      }
    },
    "enable_dark_mode": {
      "key": "enable_dark_mode",
      "state": "ON",
      "version": 1,
      "fallthrough": {
        "value": true
      }
    }
  }
}
```

Якщо ETag збігається з поточним станом на сервері, сервер повертає порожню відповідь `304 Not Modified`, усуваючи необхідність повторно десеріалізувати великі JSON-дерева правил.

---

## 3. Streaming API: Негайне сповіщення про зміну стану (SSE / WebSocket)

Для підтримки операційних рубильників (Ops Toggles / Emergency Kill-Switches) SDK відкриває довгоживуче з'єднання Server-Sent Events (SSE). Це дозволяє доставити сигнал про зміну стану прапорця до всіх підключених процесів за `< 100 ms`.

### Endpoint: `GET /api/v1/flags/stream`

**Протокол обробки розриву з'єднання (Reconnection Protocol):**
Якщо SSE-з'єднання розривається через мережевий збій, SDK переходить у режим зворотної експоненційної паузи з рандомізованим віконним сміщенням (Jittered Exponential Backoff):

```
Backoff_Time = min(Max_Backoff, Base_Backoff * 2^Attempt) + Random_Jitter
```

Під час розриву зв'язку SDK продовжує оцінювати прапорці за останнім збереженим знімком ruleset у пам'яті.

**Формат подій SSE:**

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

event: flag_updated
data: {"flagKey": "smart_lock_v2_algorithm", "version": 4, "state": "OFF", "reason": "AUTOMATED_CANARY_ROLLBACK"}

event: ruleset_reload
data: {"version": 4029, "etag": "W/\"4029-abc1234\""}
```

---

## 4. REST API Управління: Автоматичний аналіз та автовідкат (CI/CD Control Plane)

Конвеєр канарейкового випуску (Spinnaker / Argo Rollouts / CI Runner) взаємодіє з панеллю управління прапорцями через адмінський REST API для поступового збільшення відсотка розкочування або негайного аварійного скасування.

### PATCH `/api/v1/admin/flags/{flagKey}/rollout`

Оновлює відсоток розкочування канарейкової функції після успішного проходження чергової фази спостереження.

**Запит (JSON):**

```json
{
  "state": "PERCENTAGE_ROLLOUT",
  "rolloutPercentage": 25,
  "reason": "Automated Canary Analysis Phase 2 PASSED (SLO 99.9% p99 < 50ms)"
}
```

**Відповідь `200 OK` (JSON):**

```json
{
  "flagKey": "smart_lock_v2_algorithm",
  "state": "PERCENTAGE_ROLLOUT",
  "rolloutPercentage": 25,
  "previousRolloutPercentage": 10,
  "version": 5,
  "updatedBy": "canary-pipeline-bot"
}
```

### POST `/api/v1/admin/flags/{flagKey}/kill`

Операційний вимикач (Emergency Kill-Switch): негайно вимикає прапорець на 0% усім користувачам системи.

**Запит (JSON):**

```json
{
  "reason": "CANARY_METRICS_ANOMALY: HTTP 503 error rate spiked to 2.4% on 10% canary cohort"
}
```

**Відповідь `200 OK` (JSON):**

```json
{
  "flagKey": "smart_lock_v2_algorithm",
  "state": "OFF",
  "rolloutPercentage": 0,
  "version": 6,
  "killedAt": "2026-08-18T09:14:22Z"
}
```

---

## 5. Контракт обробки помилок та резервування (Fallback Semantics)

У разі виникнення будь-яких збоїв інфраструктури прапорців системи (мережеві таймаути, помилки десеріалізації, збій бази даних правил) SDK гарантує повну ізоляцію бізнес-коду від винятків.

| Сценарій збою | Поведінка SDK | HTTP / Подія | Гарантія надійності |
| :--- | :--- | :--- | :--- |
| Сервер прапорців недоступний (`5xx` або Timeout) | Повертає `defaultValue` з коду або зі стану локального диск-кешу | HTTP 503 / Socket Error | `is_enabled()` **ніколи не викидає виняток** у бізнес-код |
| Прапорець відсутній у Ruleset | Повертає `defaultValue` (типово `false`) | - | Подія телеметрії `OFF_FALLBACK` надсилається у буфер |
| Мережевий розрив SSE-стріму | Перехід на HTTP Polling раз на 15 секунд + сліпа експоненційна пауза (Jittered Backoff) | Net Reconnect | SDK продовжує працювати на останньому валідному знімку |
| Помилка десеріалізації JSON правил | Повертає останній валідний Ruleset із пам'яті | Log Error | Пошкоджений конфіг відраховується, але не ламає запуск |

### Захист персональних даних та анонімізація аудиту

Контекст оцінки прапорців часто обробляє ідентифікатори користувачів. Для дотримання вимог безпеки та захисту персональних даних (GDPR / HIPAA) SDK підтримує анонімізацію ідентифікаторів перед відправкою телеметрії на центральний сервер:
1. **Хешування ідентифікаторів на боці SDK:** перед відправкою у звіт телеметрії `userId` пропускається через SHA-256 із локальною сіллю компанії.
2. **Фільтрація атрибутів (Attribute Sanitization):** атрибути з позначкою `sensitive: true` беруть участь у локальній оцінці правил, але повністю виключаються з пакетів моніторингу та логів.

---

## 6. Метрики та телеметрія оцінки (Observability Contract)

Для забезпечення автоматичного канарейкового аналізу SDK збирає асинхронні лічильники оцінки прапорців. Телеметрія групується в пам'яті і надсилається на контрольний ендпойнт пакетним викликом (batch push) кожні 60 секунд.

### POST `/api/v1/metrics/evaluations`

**Схема пакета телеметрії (JSON):**

```json
{
  "sdkVersion": "v2.4.0",
  "host": "dh-lock-service-pod-78ab",
  "periodStart": "2026-08-18T09:10:00Z",
  "periodEnd": "2026-08-18T09:11:00Z",
  "counts": [
    {
      "flagKey": "smart_lock_v2_algorithm",
      "variation": "true",
      "count": 1420
    },
    {
      "flagKey": "smart_lock_v2_algorithm",
      "variation": "false",
      "count": 12780
    }
  ]
}
```

Ці телеметричні дані дозволяють системі моніторингу звірити реальний статистичний розподіл користувачів (наприклад, 10% vs 90%) із заданими параметрами в правила розкочування. Якщо фактичний відсоток відхиляється через помилки в алгоритмах ідентифікації сесій, конвеєр генерує сповіщення про девіацію конфігурації.

---

## 7. Рольовий доступ та аудит змін конфігурації (RBAC & Audit Trail)

Будь-яка зміна стану прапорця в адмінському REST API або через веб-панель фіксується у незмінному журналі аудиту (Audit Log).

### Політики доступу (RBAC):
- **Release Engineer:** має права на зміну відсотків канарейкового розкочування (`PATCH /api/v1/admin/flags/{key}/rollout`).
- **SecOps / Incident Commander:** має привілейоване право активації аварійного вимикача (`POST /api/v1/admin/flags/{key}/kill`).
- **CI/CD Service Account:** автоматичний бот канарейкового аналізу з обмеженим токеном, допущеним лише до конкретного реєстру релізних прапорців.

Кожен запит на зміну стану прапорця вимагає обов'язкового зазначення поля `reason`, яке зберігається в системі спостережності поруч із ідентифікатором оператора та timestamp зміни.
