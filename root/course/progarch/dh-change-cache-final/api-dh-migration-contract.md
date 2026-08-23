# 📋 Специфікація контракту міграції та когерентності кешу DH

Ця вставка містить офіційну специфікацію контрактів, подій та параметрів конфігурації для 4-фазної zero-downtime міграції цифрового твіна Digital Homes (з Варіанта Б у Варіант В) та забезпечення когерентності кешу. Документ визначає точну структуру подій інвалідації, заголовки HTTP/gRPC для забезпечення гарантії Read-Your-Writes, формат записів у реєстрі точок неповернення (ADR), механізм обробки аварійних сигналів Dead Letter Queue (DLQ), розширені метрики спостережливості Prometheus та захисні фітнес-функції для CI/CD.

---

## 1. Специфікація подій інвалідації кешу (Kafka Event Schema)

Усі події зміни стану цифрового твіна відправляються в Kafka топік `dh.twin.events.v1` через паттерн Transactional Outbox. Це забезпечує атомарність між оновленням бази даних Твіна В та публікацією події в брокер повідомлень (гарантія доставки *at-least-once*).

Для збереження суворого порядку обробки подій у межах одного будинку ключ партиціонування Kafka (Partition Key) розраховується як послідовний хеш від `homeId` за допомогою алгоритму MurmurHash3. Це гарантує, що всі події конкретного дому потрапляють у ту саму партицію і вичитуються єдиним воркером інвалідації послідовно.

### 1.1. Повний канонічний JSON Schema події `twin.state_changed`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "TwinStateChangedEvent",
  "description": "Подія оновлення стану цифрового твіна Digital Homes для інвалідації кешу та синдикації",
  "type": "object",
  "required": [
    "eventId",
    "homeId",
    "deviceId",
    "versionSeq",
    "etag",
    "observedAtMs",
    "updatedAtMs",
    "changeSource",
    "payload"
  ],
  "properties": {
    "eventId": {
      "type": "string",
      "format": "uuid",
      "description": "Унікальний ідентифікатор події для ідемпотентної обробки"
    },
    "homeId": {
      "type": "string",
      "pattern": "^home-[a-f0-9]{8}$",
      "description": "Канонічний ідентифікатор будинку"
    },
    "deviceId": {
      "type": "string",
      "pattern": "^dev-[a-f0-9]{8}$",
      "description": "Ідентифікатор пристрою, який ініціював зміну стану"
    },
    "versionSeq": {
      "type": "integer",
      "minimum": 1,
      "description": "Монотонно зростаючий версійний лічильник твіна даного будинку"
    },
    "etag": {
      "type": "string",
      "description": "Версійний хеш стану для перевірки збігу у HTTP-запитах"
    },
    "observedAtMs": {
      "type": "integer",
      "description": "Timestamp (UNIX ms) фізичного виміру на пристрої"
    },
    "updatedAtMs": {
      "type": "integer",
      "description": "Timestamp (UNIX ms) первинної фіксації у сховищі Твіна В"
    },
    "changeSource": {
      "type": "string",
      "enum": ["device_telemetry", "user_action", "automation_rule", "cloud_sync", "migration_backfill"],
      "description": "Джерело ініціації зміни стану"
    },
    "payload": {
      "type": "object",
      "additionalProperties": true,
      "description": "Схема модифікованих атрибутів стану"
    }
  }
}
```

### 1.2. Семантика полів події та правила обробки

1. **`versionSeq` (Version Sequence)**: Суворо монотонне 64-бітне ціле число. Кожен новий запис у сховище Твіна В інкрементує `versionSeq` на одиницю у межах одного `homeId`. Обробник кешу (Cache Invalidator) мусить виконати перевірку: якщо `event.versionSeq <= cache.versionSeq`, подія ігнорується як застаріла або дубльована.
2. **`etag`**: Генерується за допомогою SHA-256 від канонізованого JSON-строка payload і короткого хешу `versionSeq`. Уживається у веб-клієнтах для умовних HTTP-запитів `If-None-Match`.
3. **`changeSource`**: Дозволяє кеш-інвалідатору застосовувати різні пріоритети очищення. Наприклад, події від `user_action` викликають негайне вигасання ключа, тоді як події від `migration_backfill` оновлюють кеш без генерування пуш-нотифікацій.

---

## 2. Контракт Edge-заголовків для гарантії Read-Your-Writes

При взаємодії мобільного застосунку з API Gateway (BFF) виникає часова асиметрія: після виконання модифікуючого запиту `POST` або `PUT` наступний читацький запит `GET` може потрапити на Edge-вузол кешування раніше, ніж Kafka-подія інвалідації встигне оновити запис у Redis.

Щоб запобігти зчитуванню застарілих даних автором зміни, платформою впроваджено контракт спеціалізованих HTTP/gRPC заголовків.

### 2.1. Повна специфікація HTTP-заголовків

| Назва заголовка | Формат / Тип | Напрямок | Алгоритм обробки та реакція системи |
|---|---|---|---|
| `X-DH-Min-Version` | `uint64` | Клієнт → BFF | Клієнт передає значення `versionSeq`, отримане у відповідь на попередню мутацію. Якщо кеш містить версію `< X-DH-Min-Version`, Gateway виконує bypass кешу напряму до DB Твіна В. |
| `ETag` | `string` | BFF → Клієнт | Версійний хеш у форматі `W/"v1048-b9a2"`. Дозволяє клієнту надсилати умовний запит `If-None-Match` й отримувати відповідь `304 Not Modified` при відсутності змін. |
| `X-DH-Observed-At` | `uint64` | BFF → Клієнт | UNIX timestamp у мілісекундах. Вказує час останнього фізичного виміру давача. Використовується клієнтським UI для малювання індикатора свіжості даних. |
| `X-DH-Telemetry-Lag` | `uint32` | BFF → Клієнт | Значення затримки обробки в мілісекундах (`nowMs - observedAtMs`). Вираховується Edge-вузлом і вживається для моніторингу затримки на проміжку давач → хмара. |
| `X-DH-Fallback-Used` | `boolean` | BFF → Клієнт | Прапорець, який звертає увагу на те, що під час Фази 2 міграції Твін В повернув помилку і запит був обслугований через Fallback з legacy Твіна Б. |

### 2.2. Послідовність викликів при перевірці заголовка `X-DH-Min-Version`

1. Мобільний застосунок надсилає `POST /api/v1/home/lock/unlock` для відчинення дверей.
2. Сервіс Твіна В здійснює мутацію, присвоює стану `versionSeq = 1049` і повертає `HTTP 200 OK` із заголовком `X-DH-Min-Version: 1049`.
3. Мобільний застосунок зберігає `1049` у локальному стані й при наступному `GET /api/v1/home/state` додає заголовок `X-DH-Min-Version: 1049`.
4. API Gateway читає запис з Redis. Якщо версія у Redis `1048` (подія Kafka ще в дорозі), Gateway ігнорує кеш, робить запит до Read Model Твіна В, повертає версію `1049` клієнту та асинхронно оновлює Redis.

---

## 3. Матриця фаз міграції та точок неповернення (ADR Decision Framework)

Кожна фаза 4-фазної zero-downtime міграції має суворі критерії входу, метрики готовності та визначену графіком точку неповернення (Point of No Return).

### 3.1. Деталізована матриця фазового контуру

```
Phase 0: Baseline ──> Phase 1: Dual-Write ──> Phase 2: Switch Read Primary ──> Phase 3: Contract
     │                        │                         │                            │
[Безпечно]             [Прапорець OFF]           [ТОЧКА НЕПОВЕРНЕННЯ]               [Твін Б відключено]
```

| Параметр | Phase 0 (Baseline) | Phase 1 (Dual-Write) | Phase 2 (Read Primary V) | Phase 3 (Contract) |
|---|---|---|---|---|
| **Джерело первинного запису** | Твін Б (PostgreSQL) | Твін Б (синхронно) | **Твін В (Outbox)** | Твін В |
| **Джерело первинного читання** | Твін Б | Твін Б | **Твін В** (з Fallback) | Твін В |
| **Фоновий процес** | Немає | Verification Harness (1%) | Online Backfill (500 req/s) | Архівування Твіна Б |
| **Точка неповернення** | Ні | Ні | **ТАК (після 1-го нового запису)** | ТАК |
| **Процедура відкату (Rollback)** | N/A | Вимкнути `dual_write_flag` | Реверсний backfill даних В → Б | Відновлення з резервної копії |
| **Критерій переходу на наступну фазу** | Повна готовність коду Твіна В | `mismatch_rate < 0.001%` протягом 48 год | `backfill_progress == 100%` & `fallback == 0` (72h) | Твін Б повністю зупинений і відключений |
| **Схема інвалідації кешу** | Write-Through у Redis | Write-Through Б + Подійна В | Подійна В + Versioned Keys | Подійна В + Versioned Keys |

### 3.2. Алгоритм дій при спрацьовуванні відкату (Rollback Protocol)

1. **Фаза 1 (Dual-Write)**: Якщо метрика `twin_mismatch_total` зростає через баг у коді Твіна В, черговий інженер переключає Feature Flag `dual_write_enabled = false`. Запис у Твін В зупиняється. Система повертається у Фазу 0 без втрати даних, оскільки джерелом правди залишався Твін Б.
2. **Фаза 2 (Switch Read Primary)**: Якщо під навантаженням у Твіні В виявлено витік пам'яті або зростання затримки, інженер вмикає `force_read_legacy_b = true`. Читання повертається до Твіна Б. Однак усі нові записи, які пройшли в Твін В за час перебування у Фазі 2, мають бути вичитані спеціальним реверсним воркером backfill (CDC з Твіна В у Б) перед остаточним вимкненням Твіна В.

---

## 4. Конфігураційна специфікація та змінні середовища

Вся поведінка фазового фасадера та захисних механізмів кешування керується єдиним YAML-файлом конфігурації із підтримкою гарячого перезавантаження без перезапуску процесів.

```yaml
digital_homes:
  migration:
    current_phase: "Phase1_DualWrite"  # Варіанти: Phase0_Baseline, Phase1_DualWrite, Phase2_ReadPrimaryV_Backfill, Phase3_Contract
    dual_write_enabled: true
    verification:
      enabled: true
      sample_rate: 0.01                # 1% читацького трафіку перевіряється в Parallel Run
      alert_mismatch_threshold: 5      # Поріг розбіжностей на хвилину для алера в PagerDuty
    backfill:
      batch_size: 500
      max_rate_per_sec: 500
      min_rate_per_sec: 50
      db_p99_latency_threshold_ms: 50  # Динамічний тротлінг: зниження швидкості при лазі БД
      db_cpu_threshold_percent: 75
    fallback:
      enabled: true
      max_retries: 2
      circuit_breaker:
        failure_threshold: 10
        reset_timeout_ms: 15000

  cache:
    redis:
      key_prefix: "dh:twin:v2"
      soft_ttl_ms: 5000
      hard_ttl_ms: 30000
      jitter_range_ms: 750             # ±750мс для відсікання масового вигасання ключів
    singleflight:
      enabled: true
      wait_timeout_ms: 2000
    version_invalidation:
      enabled: true
      strict_sequence_check: true
```

---

## 5. Обробка помилок та політика Dead Letter Queue (DLQ)

При асинхронній інвалідації кешу через Kafka можливі збої: тимчасова недоступність Redis, помилки десеріалізації подій або конфлікти версій.

### 5.1. Правила маршрутизації помилок інвалідації

1. **Тимчасові помилки (Transient Errors)**: При відсутності зв'язку з Redis воркер інвалідації повторює спробу 3 рази із експоненційним відкладанням (Exponential Backoff: 100мс, 400мс, 1600мс). Якщо Redis не відповідає, воркер зупиняє зсув (offset) партиції Kafka, запобігаючи втраті подій.
2. **Незворотні помилки (Poison Pills)**: При помилці JSON Schema валідації подія відправляється у Dead Letter Queue топік `dh.twin.events.dlq`. Метрика `twin_dlq_events_total` інкрементується.
3. **Аварійне очищення при переповненні DLQ**: Якщо в DLQ потрапляє понад 1000 повідомлень за годину, запускається автоматична процедура `FlushAllCache()`, яка скидає весь Edge-кеш і примушує систему тимчасово працювати через Singleflight-читання з бази даних до усунення причин аварії.

---

## 6. Метрики спостережливості Prometheus

Для контролю здоров'я міграційного контуру та кеш-когерентності сервіси експортують наступні ключові метрики.

### 6.1. Таблиця операційних метрик

| Назва метрики | Тип | Етикетки (Labels) | Опис та цільові значення |
|---|---|---|---|
| `twin_migration_phase` | Gauge | `phase` | Поточна активна фаза міграції (0, 1, 2, 3). |
| `twin_mismatch_total` | Counter | `field`, `phase` | Кількість розбіжностей, виявлених Parallel Run верифікатором. Ціль: 0. |
| `twin_backfill_progress_ratio` | Gauge | `table` | Прогрес виконання онлайн-backfill (0.0 → 1.0). |
| `twin_fallback_requests_total` | Counter | `reason` | Кількість спрацьовувань Fallback з Твіна В на Твін Б у Фазі 2. |
| `cache_singleflight_coalesced_total` | Counter | `key_prefix` | Кількість запитів, злитих у єдиний виклик до БД паттерном Singleflight. |
| `cache_stale_events_rejected_total` | Counter | `reason` | Кількість подій інвалідації, відхилених через старіший `versionSeq`. |
| `telemetry_lag_seconds` | Histogram | `device_type` | Гістограма затримки від `observedAtMs` до фіксації в твіні. P99 < 1.5s. |

---

## 7. Фітнес-функції для автоматизованого контролю в CI/CD

Для запобігання ситуаціям, коли розробники нового сервісу випадково звертаються до старого Твіна Б в оминення фазового фасаду `TwinMigrationFacade`, у CI-пайплайн вбудовано захисні фітнес-тести на основі аналізу графа залежностей.

```typescript
// ArchUnit / Static Analysis Fitness Test
import { ArchRuleBuilder } from "@archunit/core";

describe("Architecture Boundary & Migration Fitness Tests", () => {
  it("BFF modules MUST NOT access Legacy Twin B directly", async () => {
    const rule = ArchRuleBuilder.classes()
      .that()
      .resideInAPackage("..bff..")
      .should()
      .onlyDependOnClassesThat()
      .resideInAnyPackage("..facade..", "..dto..", "java..");

    await rule.check();
  });

  it("All Twin state mutations MUST generate Outbox events", async () => {
    const mutationMethods = findAnnotatedMethods("@TwinMutation");
    for (const method of mutationMethods) {
      expect(method.hasOutboxTransaction()).toBe(true);
    }
  });
});
```

Поточні фітнес-тести гарантують, що після завершення Фази 3 будь-яка спроба затягнути код legacy-твіна Б у нові збірки призведе до автоматичної зупинки CI/CD конвеєра.
