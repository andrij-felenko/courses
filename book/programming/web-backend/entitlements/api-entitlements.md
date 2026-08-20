# 📋 Інтерфейс служби ентайтлментів: контракти перевірки, заголовки та події

<preknowlist>
- [Ентайтлменти](book:programming/entitlements) — комерційні права, булеві шлюзи, статичні ліміти та метричні квоти організації.
- [REST](book:programming/rest-api) — стандартні статусні коди, заголовки та структура тіла HTTP-відповідей.
- [Webhooks](book:programming/webhooks) — отримання та обробка асинхронних подій від сторонніх систем.
- [Ідемпотентність методів](book:programming/api-idempotency) — збереження стану операцій при повторних викликах.
</preknowlist>

Служба ентайтлментів виступає центральним арбітром комерційного доступу в розподіленій системі. Вона забезпечує взаємодію між двома світами: зовнішньою комерційною площиною (платіжні шлюзи, білінгові платформи, підписки, рахунки) та внутрішньою технічною площиною виконання (API Gateway, мікросервіси, фонові обробники задач, клієнтські застосунки).

Без чіткого, стабільного контракту інтерфейсу будь-яка зміна платіжного шлюзу (наприклад, міграція зі Stripe на Adyen чи Zuora) вимагає переписування десятків мікросервісів. Служба ентайтлментів повністю ізолює внутрішню систему від зовнішніх білінгових моделей, надаючи уніфіковані інтерфейси перевірки прав, керування квотами та обробки подій.

Щоб забезпечити надійну й швидку роботу цієї підсистеми, інтерфейс служби ентайтлментів розділяють на шість чітких контрактів:
1. **Внутрішній API оцінки та резервування (Evaluation & Quota API):** високоефективний синхронний RPC/REST-інтерфейс для перевірки булевих шлюзів і резервування періодичних квот.
2. **Публічний клієнтський API отримання стану (Client Capabilities API):** надання зліпка можливостей для рендерингу інтерфейсу користувача.
3. **Публічний HTTP-контракт заголовків та помилок:** машинночитні статуси, інформаційні заголовки та структуровані тіла відповідей за стандартом RFC 7807, які повертаються кінцевим користувачам та інтеграторам.
4. **Вхідний контракт синхронізації білінгу (Billing Webhook Ingestion):** захищені криптографічним підписом точки входу для отримання асинхронних подій від платіжних провайдерів.
5. **Вихідна шина системних подій (Outbound Event Bus):** публікація подій зміни прав для синхронізації кешів, надсилання сповіщень адміністраторам та оновлення інтерфейсу в реальному часі.
6. **Контракт клієнтського SDK та політика деградації:** правила кешування, обробки збоїв та трасування викликів.

Нижче наведено повну технічну специфікацію кожного з цих інтерфейсів із детальним описом параметрів, інваріантів та крайових випадків.

---

## 1. Внутрішній API оцінки прав (Evaluation API)

Внутрішній API призначений для виклику з API Gateway або сервісних проміжних шарів (*middleware*) перед виконанням бізнес-логіки. Для мінімізації затримок цей API підтримує як високошвидкісний gRPC (Protobuf), так і стандартний HTTP/JSON.

### Специфікація Protobuf (gRPC Contract)

```protobuf
syntax = "proto3";

package entitlements.v1;

service EntitlementService {
  rpc Evaluate(EvaluateRequest) returns (EvaluateResponse);
  rpc ReserveQuota(ReserveQuotaRequest) returns (ReserveQuotaResponse);
  rpc ReleaseQuota(ReleaseQuotaRequest) returns (ReleaseQuotaResponse);
}

message CheckRequirement {
  enum CheckType {
    CHECK_TYPE_UNSPECIFIED = 0;
    CHECK_TYPE_FEATURE = 1;
    CHECK_TYPE_LIMIT = 2;
  }
  CheckType type = 1;
  string key = 2;
  int64 proposed_value = 3;
}

message EvaluateRequest {
  string tenant_id = 1;
  repeated CheckRequirement checks = 2;
}

message CheckResult {
  bool allowed = 1;
  string reason = 2;
  string required_plan = 3;
  int64 current_limit = 4;
  int64 remaining_capacity = 5;
}

message EvaluateResponse {
  string tenant_id = 1;
  int64 version = 2;
  bool is_read_only = 3;
  map<string, CheckResult> results = 4;
}

message ReserveQuotaRequest {
  string tenant_id = 1;
  string metric = 2;
  int64 amount = 3;
  string idempotency_key = 4;
}

message ReserveQuotaResponse {
  bool allowed = 1;
  string reservation_id = 2;
  string metric = 3;
  int64 limit = 4;
  int64 consumed = 5;
  int64 remaining = 6;
  string reset_at = 7;
  bool overage_allowed = 8;
}

message ReleaseQuotaRequest {
  string tenant_id = 1;
  string metric = 2;
  string reservation_id = 3;
  int64 amount = 4;
}

message ReleaseQuotaResponse {
  bool released = 1;
  string metric = 2;
  int64 current_usage = 3;
}
```

---

### REST-інтерфейс: `POST /v1/entitlements/evaluate`

Виконує пакетну перевірку набору булевих функцій, статичних лімітів та актуального статусу для організації за один мережевий виклик.

#### Параметри запиту:

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `tenant_id` | `string` | Так | Унікальний ідентифікатор організації (наприклад, `org_982bca10`). |
| `checks` | `array` | Так | Масив вимог для перевірки (від 1 до 50 елементів у пакеті). |
| `checks[].type` | `string` | Так | Тип перевірки: `feature` (булеве право) або `limit` (статичний ліміт). |
| `checks[].key` | `string` | Так | Системний ключ можливості або ліміту (наприклад, `sso`, `max_seats`). |
| `checks[].proposed_value`| `integer` | Ні | Запитуване нове значення (використовується для типу `limit`). |

**Приклад тіла запиту:**

```json
{
  "tenant_id": "org_982bca10",
  "checks": [
    { "type": "feature", "key": "sso" },
    { "type": "feature", "key": "audit_logs" },
    { "type": "limit", "key": "max_projects", "proposed_value": 12 }
  ]
}
```

#### Параметри відповіді (`200 OK`):

| Поле | Тип | Опис |
|---|---|---|
| `tenant_id` | `string` | Ідентифікатор перевіреної організації. |
| `version` | `integer` | Монотонна мітка версії зліпка (Unix timestamp в мілісекундах). |
| `is_read_only` | `boolean` | Чи заблоковано організацію на запис через несплату або даунгрейд. |
| `results` | `object` | Карта результатів перевірки за кожним переданим ключем. |
| `results[key].allowed` | `boolean` | Чи дозволена операція за цим критерієм. |
| `results[key].reason` | `string` | Машинночитний код причини (`included_in_plan`, `requires_plan_upgrade`, `limit_reached`). |
| `results[key].required_plan` | `string` | Мінімальний тариф, необхідний для відкриття цієї функції (опціонально). |

**Приклад тіла відповіді:**

```json
{
  "tenant_id": "org_982bca10",
  "version": 1724112000000,
  "is_read_only": false,
  "results": {
    "feature:sso": {
      "allowed": true,
      "reason": "included_in_plan"
    },
    "feature:audit_logs": {
      "allowed": false,
      "reason": "requires_plan_upgrade",
      "required_plan": "enterprise"
    },
    "limit:max_projects": {
      "allowed": true,
      "current_limit": 20,
      "proposed_value": 12,
      "remaining_capacity": 8
    }
  }
}
```

---

### `POST /v1/entitlements/quota/reserve`

Атомарно перевіряє наявність залишку та резервує одиниці періодичної метричної квоти за допомогою транзакційного лічильника.

#### Параметри запиту:

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `tenant_id` | `string` | Так | Ідентифікатор організації. |
| `metric` | `string` | Так | Назва метрики (наприклад, `monthly_api_calls`, `storage_bytes`). |
| `amount` | `integer` | Так | Кількість одиниць для резервування (за замовчуванням `1`). |
| `idempotency_key` | `string` | Так | Унікальний ключ ідемпотентності клієнтського запиту. |

**Приклад запиту:**

```json
{
  "tenant_id": "org_982bca10",
  "metric": "monthly_api_calls",
  "amount": 1,
  "idempotency_key": "req_8819af92-0b1a-4d43"
}
```

#### Відповідь при наявності квоти (`200 OK`):

```json
{
  "allowed": true,
  "reservation_id": "res_9941a82f",
  "metric": "monthly_api_calls",
  "limit": 500000,
  "consumed": 384120,
  "remaining": 115880,
  "reset_at": "2026-09-01T00:00:00Z"
}
```

#### Відповідь при вичерпанні квоти (`200 OK` із прапорцем `allowed: false`):

```json
{
  "allowed": false,
  "metric": "monthly_api_calls",
  "limit": 500000,
  "consumed": 500000,
  "remaining": 0,
  "reset_at": "2026-09-01T00:00:00Z",
  "overage_allowed": false
}
```

---

### `POST /v1/entitlements/quota/release`

Звільняє раніше зарезервовану квоту у разі аварійного завершення бізнес-обробника.

#### Параметри запиту:

```json
{
  "tenant_id": "org_982bca10",
  "metric": "monthly_api_calls",
  "reservation_id": "res_9941a82f",
  "amount": 1
}
```

#### Відповідь (`200 OK`):

```json
{
  "released": true,
  "metric": "monthly_api_calls",
  "current_usage": 384119
}
```

---

## 2. Публічний клієнтський API отримання стану (Client Capabilities API)

Для веб-фронтенду (Single Page Applications на React, Vue чи мобільних застосунків) служба надає оптимізований ендпоінт, який повертає повну карту можливостей поточного користувача.

### `GET /v1/me/capabilities`

Повертає скомпільований зліпок доступних функцій, залишок лімітів і стан підписки для відображення елементів інтерфейсу:

**Відповідь (`200 OK`):**

```json
{
  "tenant_id": "org_982bca10",
  "plan_name": "Pro Growth Plan",
  "status": "active",
  "features": {
    "sso": true,
    "custom_domains": true,
    "audit_logs": false,
    "export_csv": true
  },
  "limits": {
    "seats": { "current": 14, "max": 20 },
    "projects": { "current": 8, "max": 10 }
  },
  "quotas": {
    "api_calls": { "consumed": 384120, "max": 500000, "reset_at": "2026-09-01T00:00:00Z" }
  },
  "upgrade_options": [
    {
      "feature": "audit_logs",
      "target_plan": "enterprise",
      "title": "Upgrade to Enterprise for 90-day Audit Logs"
    }
  ]
}
```

### Принципи відображення в інтерфейсі (Product-Led Growth):
1. **Не ховати функції, а деактивувати з підказкою:** замість повного приховування кнопок недоступних функцій (наприклад, кнопки «Налаштувати SAML SSO»), інтерфейс показує їх неактивними з піктограмою замка та випливаючою підказкою (*Upgrade Tooltip*). Це стимулює користувачів переходити на вищі тарифи.
2. **Попередження про наближення ліміту:** коли кількість створених проєктів досягає 8 із 10 (80%), у верхній частині панелі керування з'являється інформаційне повідомлення з пропозицією докупити додатковий пакет проєктів.

---

## 3. Публічні HTTP-заголовки стану квот

Для всіх ендпоінтів, що споживають метричні ресурси тарифу, API Gateway додає стандартний набір HTTP-заголовків до відповіді клієнту. Це дозволяє клієнтським SDK автоматично відстежувати залишок ресурсів без додаткових опитувань:

| Заголовок | Тип | Опис | Приклад |
|---|---|---|---|
| `X-Entitlement-Limit` | Ціле число | Загальний ліміт квоти на поточний розрахунковий період | `500000` |
| `X-Entitlement-Remaining` | Ціле число | Залишок невикористаних одиниць у поточному періоді | `115880` |
| `X-Entitlement-Reset` | Unix timestamp | Момент часу (в секундах), коли лічильник квоти обнулиться | `1788220800` |
| `X-Entitlement-Warning` | Рядок | Попередження про наближення до вичерпання (при залишку < 20%) | `299 - "Quota 80% consumed"` |

### Різниця між Rate Limiting та Entitlements Headers

Часто розробники плутають заголовки обмеження швидкості (`Rate-Limit`) із заголовками комерційних квот (`Entitlement-Limit`):

- **`Rate-Limit` (429 Too Many Requests):** технічне обмеження інтенсивності запитів на секунду (наприклад, 100 req/sec), призначене для захисту інфраструктури від перевантаження та DoS-атак. Воно скидається щосекунди чи щохвилини.
- **`Entitlement-Limit` (402 Payment Required):** договірне бізнес-обмеження загального обсягу споживання за розрахунковий місяць (наприклад, 500 000 викликів на місяць), яке скидається лише на початку наступного платіжного циклу.

Клієнтський SDK повинен розділяти ці два рівні: при отриманні `429` слід виконати експоненційну паузу (*backoff*), а при отриманні `402` — попередити користувача про вичерпання тарифного плану.

---

## 4. Структуровані схеми помилок (RFC 7807)

Коли запит відхиляється через обмеження тарифного плану або фінансовий статус підписки, сервер повертає машинночитну відповідь із контекстом для оновлення плану відповідно до стандарту RFC 7807 (Problem Details for HTTP APIs).

### А. Функція недоступна в поточному тарифі (`403 Forbidden`)

Повертається, коли користувач намагається виконати дію, яка заблокована булевим функціональним шлюзом:

```json
{
  "type": "https://api.example.com/errors/feature-gated",
  "title": "Feature Not Available in Current Plan",
  "status": 403,
  "detail": "Exporting audit logs requires an Enterprise subscription plan.",
  "code": "feature_gated",
  "feature": "audit_logs_export",
  "current_plan": "pro",
  "required_plan": "enterprise",
  "upgrade_url": "https://app.example.com/settings/billing/upgrade?feature=audit_logs_export"
}
```

### Б. Вичерпано періодичну квоту (`402 Payment Required`)

Повертається, коли лічильник споживання досяг максимального ліміту й режим понаднормового споживання (*overage*) вимкнено:

```json
{
  "type": "https://api.example.com/errors/quota-exceeded",
  "title": "Monthly Quota Exceeded",
  "status": 402,
  "detail": "Your organization has consumed all 500,000 monthly API calls.",
  "code": "quota_exceeded",
  "metric": "monthly_api_calls",
  "limit": 500000,
  "consumed": 500000,
  "reset_at": "2026-09-01T00:00:00Z",
  "upgrade_url": "https://app.example.com/settings/billing/add-ons?metric=api_calls"
}
```

### В. Підписка заблокована через несплату (`402 Payment Required`)

Повертається під час спроби запису, коли пільговий період після невдалого списання коштів минув:

```json
{
  "type": "https://api.example.com/errors/subscription-past-due",
  "title": "Subscription Past Due",
  "status": 402,
  "detail": "Your subscription is suspended due to unpaid invoices. Write operations are disabled.",
  "code": "subscription_suspended",
  "grace_period_expired_at": "2026-08-15T12:00:00Z",
  "billing_portal_url": "https://billing.example.com/session/sess_991823"
}
```

---

## 5. Вхідні вебхуки синхронізації білінгу

Служба ентайтлментів обробляє події від платіжного шлюзу для підтримки актуального стану комерційних контрактів.

### `POST /v1/webhooks/billing`

Приймає підписані події від білінгового провайдера.

```json
{
  "id": "evt_3N8x72Lkd82j",
  "type": "customer.subscription.updated",
  "created": 1724112000,
  "data": {
    "object": {
      "id": "sub_1M9x81",
      "customer": "cus_99182",
      "tenant_id": "org_982bca10",
      "status": "active",
      "items": [
        { "plan_id": "plan_enterprise_yearly", "quantity": 1 },
        { "addon_id": "addon_extra_seats_10", "quantity": 2 }
      ],
      "current_period_start": 1724112000,
      "current_period_end": 1755648000,
      "cancel_at_period_end": false
    }
  }
}
```

### Семантика та інваріанти обробки вебхуків:

1. **Криптографічна верифікація:** обробник витягує часову мітку `t` та підпис `v1` із заголовка `Stripe-Signature`. Він обчислює очікуваний HMAC-SHA256 від рядка `${t}.${raw_payload}` і порівнює його за сталий час. Запити з часовим зсувом більше 300 секунд відхиляються для захисту від атак повтору (*Replay Attacks*).
2. **Ідемпотентність:** кожен унікальний `id` події записується в реляційну таблицю `processed_events` з первинним ключем `event_id`. Повторне надходження того самого ідентифікатора повертає `200 OK` без повторного запуску компіляції.
3. **Асинхронна рекомпіляція:** воркер викликає `resolveSnapshot(tenant_id)` і записує новий зліпок у Redis.
4. **Інвалідація кешу:** публікується подія в шину повідомлень для скидання локальних L1-кешів інстансів.

---

## 6. Внутрішні системні події (Event Bus)

Для сповіщення інших мікросервісів та UI-клієнтів служба публікує події в шину повідомлень:

| Назва події | Коли емітиться | Призначення |
|---|---|---|
| `entitlement.snapshot_updated` | При зміні плану, додаванні аддонів або зміні статусу | Інвалідація L1/L2 кешів у всіх інстансах застосунку |
| `entitlement.quota_warning` | При досягненні 80% та 95% місячного ліміту | Відправка email-сповіщення адміністраторам компанії |
| `entitlement.quota_exceeded` | При вичерпанні 100% ліміту | Блокування нових запитів і виведення банера в UI |
| `entitlement.grace_period_started` | При першій невдалій спробі списання коштів | Активація таймера пільгового періоду (7-14 днів) |

### Схема повідомлення `entitlement.snapshot_updated`:

```json
{
  "event_id": "evt_ent_991823a",
  "event_type": "entitlement.snapshot_updated",
  "tenant_id": "org_982bca10",
  "version": 1724112000000,
  "timestamp": "2026-08-20T01:00:00Z",
  "changes": {
    "features_added": ["sso", "audit_logs"],
    "features_removed": [],
    "limits_changed": {
      "max_seats": { "old": 20, "new": 50 }
    }
  }
}
```

---

## 7. Контракт клієнтського SDK та політика деградації

Клієнтський SDK, що вбудовується в інші мікросервіси платформи, реалізує такі обов'язкові інваріанти:

1. **Локальний кеш L1 із коротким TTL:** SDK зберігає отриманий зліпок у локальній пам'яті на 15–30 секунд. Це усуває 99.9% міжсервісних викликів для перевірки булевих прапорців.
2. **Підписка на інвалідацію:** SDK слухає канал Redis Pub/Sub або Kafka топік `entitlements.invalidation`. При отриманні повідомлення відповідний `tenant_id` негайно видаляється з локального кешу.
3. **Політика відмовостійкості (Fallback Policy):**
   - Якщо служба ентайтлментів недоступна, SDK використовує останній відомий кешований зліпок (*stale cache*), навіть якщо його TTL минув.
   - Якщо зліпок взагалі відсутній у пам'яті, SDK повертає базовий захисний набір прав (*default safe tier*), дозволяючи лише критичні операції читання.
4. **Вбудоване трасування:** кожен виклик перевірки автоматично створює OpenTelemetry спан `entitlement.check` із тегами `feature`, `tenant_id` та `allowed`.
