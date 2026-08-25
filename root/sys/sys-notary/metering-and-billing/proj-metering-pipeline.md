# ⚙️ Конвеєр обліку: від прийому події до фіксації в реєстрі

Спроба вести білінг простим оновленням балансу в реляційній базі (`UPDATE accounts SET balance = balance - cost`) ламається за першого ж реального навантаження. Коли сотні паралельних воркерів списують кошти з одного облікового запису компанії, рядкові блокування (row-level locks) перетворюють конкурентний бекенд на вузьке пляшкове горло, збільшуючи затримку обробки запиту в десятки разів. Якщо ж виклик API завершується таймаутом чи збоєм мережі, повторна спроба списує кошти вдруге, або навпаки — безслідно губить спожиті ресурси.

Причина цієї кризи криється в архітектурному розриві між вимогами до швидкості обробки веб-запитів і вимогами до фінансової строгості. Швидкий шлях виконання запиту (fast path) вимагає субмілісекундних перевірок лімітів і нульових блокувань бази даних, тоді як фінансовий облік вимагає непорушного аудиторського сліду, захисту від гонок і гарантій відсутності втрат подій. Спроба поєднати обидва завдання в одному синхронному обробнику запиту призводить до взаємних блокувань пулу з'єднань, деградації продуктивності та фінансових розбіжностей під час першого ж збою мережі.

Тут ми побудуємо повноцінний, відмовостійкий конвеєр обліку (metering) і тарифікації (rating), який вирішує шість критичних інженерних завдань:

1. **Атомарно дедуплікує вхідні події споживання** за ідемпотентним ключем на швидкості потоку без блокування клієнтських запитів.
2. **Буферизує та пакетує події (Batch Flush Loop)** для зменшення мережевого навантаження на базу даних.
3. **Реалізує шаблон резервування кредитів (Credit Hold / Reservation)** для захисту від перевитрат під час тривалих або непередбачуваних за вартістю операцій.
4. **Агрегує метрики у вікнах** і розраховує пошарову вартість у точній цілочисельній арифметиці без похибок дробових чисел.
5. **Фіксує фінансовий результат у незмінному реєстрі подвійного запису (Double-Entry Ledger)**, гарантуючи нульовий дисбаланс, повний аудит і неможливість подвійного списання.
6. **Коректно обробляє запізнілі події та сторнування (Reconciliation & Compensations)** без порушення вже закритих фінансових періодів.

## Схема сховища: незмінні журнали та атомарні обмеження

Конвеєр спирається на три базові реляційні таблиці: журнал сирих подій з ідемпотентним фільтром, таблицю активних резервацій квот і журнал бухгалтерських проведень.

Розглянемо призначення кожного стовпця та індексу:

- `usage_events`: діє як незмінний вхідний буфер (staging log). Кожна подія містить унікальний `idempotency_key`, який формується на стороні джерела події (воркера або API-шлюзу). Унікальне обмеження на цей стовпець гарантує, що база даних апаратно відхилить будь-який дублікат події, що виник через мережевий повтор запиту.
- `credit_reservations`: обслуговує короткоживучі блокування квот перед початком дорогих обчислень. Стовпець `expires_at` забезпечує захист від "зависання" коштів, якщо процес, який ініціював роботу, аварійно завершиться до виклику фіналізації.
- `ledger_entries`: серце фінансового обліку. У цій таблиці принципово відсутні команди `UPDATE` та `DELETE` — будь-яка зміна фінансового стану записується виключно через операцію `INSERT` двох або більше збалансованих проводок.

```sql
-- 1. Сирий журнал подій споживання з дедуплікацією
CREATE TABLE usage_events (
    event_id          TEXT PRIMARY KEY,          -- UUID або зовнішній ідентифікатор події
    idempotency_key   TEXT NOT NULL UNIQUE,      -- SHA-256 відбиток (tenant_id + request_id + source)
    tenant_id         TEXT NOT NULL,
    metric_name       TEXT NOT NULL,             -- 'api_requests', 'llm_tokens', 'egress_bytes'
    quantity          BIGINT NOT NULL,           -- обсяг споживання (ціле число)
    occurred_at       TIMESTAMPTZ NOT NULL,      -- точний час події на клієнті/воркері
    ingested_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    properties        JSONB                      -- метадані (регіон, модель, тип операції)
);

CREATE INDEX idx_usage_events_tenant_window 
ON usage_events (tenant_id, metric_name, occurred_at);

-- 2. Активні резервації кредитів (Hold Pattern)
CREATE TABLE credit_reservations (
    reservation_id    TEXT PRIMARY KEY,
    tenant_id         TEXT NOT NULL,
    reserved_micros   BIGINT NOT NULL,           -- заблокована сума в мікродоларах ($1 = 1 000 000)
    state             TEXT NOT NULL CHECK (state IN ('active', 'settled', 'released')),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at        TIMESTAMPTZ NOT NULL       -- тайм-аут автоскасування завислого холду
);

-- 3. Незмінний журнал подвійного запису (Ledger)
CREATE TABLE ledger_entries (
    entry_id          BIGSERIAL PRIMARY KEY,
    transaction_id    TEXT NOT NULL,             -- логічне групування двох проводок (дебет і кредит)
    account_id        TEXT NOT NULL,             -- 'liability:customer_123', 'revenue:api_usage'
    account_type      TEXT NOT NULL CHECK (account_type IN ('asset', 'liability', 'revenue', 'expense')),
    amount_micros     BIGINT NOT NULL,           -- додатне для збільшення, від'ємне для зменшення
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    reference_id      TEXT                       -- зв'язок з event_id, reservation_id чи інвойсом
);

CREATE INDEX idx_ledger_account ON ledger_entries (account_id, created_at);
```

## Крок 1: Обробка та ідемпотентний прийом події

Подія споживання створюється безпосередньо у воркері після виконання операції. Оскільки мережеві збої та таймаути є неминучими в розподіленій системі, клієнти та внутрішні черги завдань використовують повтори з експоненційним відступом (retries with backoff). Без надійного фільтра дедуплікації кожен повторний запит призводив би до повторного нарахування за ту саму послугу.

Щоб забезпечити ідемпотентність, подія повинна мати детермінований відбиток `idempotency_key`. Відбиток розраховується як криптографічний геш SHA-256 від комбінації незмінних параметрів: ідентифікатора клієнта (`tenant_id`), унікального ідентифікатора виклику (`request_id`) та назви підсистеми або вузла-джерела (`source`). Якщо два повідомлення мають однаковий відбиток, конвеєр гарантовано розпізнає в них дублікат.

Під час надходження події рушій прийому намагається зберегти ключ у сховищі ідемпотентності. Якщо ключ новий, подія негайно приймається до черги обробки. Якщо такий ключ уже було зафіксовано раніше, запит кваліфікується як повтор і безпечно ігнорується без виклику повторної тарифікації:

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <optional>
#include <cstdint>
#include <chrono>
#include <vector>
#include <unordered_set>
#include <iomanip>
#include <sstream>

// Фіксована точність: 1 USD = 1 000 000 мікродоларів
using CurrencyMicros = int64_t;

struct UsageEvent {
    std::string event_id;
    std::string idempotency_key;
    std::string tenant_id;
    std::string metric_name;
    uint64_t quantity;
    std::chrono::system_clock::time_point occurred_at;
};

enum class IngestResult {
    Accepted,
    DuplicateIgnored,
    InvalidData
};

class EventIngestEngine {
private:
    // У продакшені це первинний унікальний індекс бази даних або Redis Bloom-фільтр
    std::unordered_set<std::string> seen_idempotency_keys_;

public:
    IngestResult ingest_event(const UsageEvent& event) {
        if (event.tenant_id.empty() || event.metric_name.empty() || event.quantity == 0) {
            return IngestResult::InvalidData;
        }

        // Атомарна перевірка та додавання ключа ідемпотентності
        auto [it, inserted] = seen_idempotency_keys_.insert(event.idempotency_key);
        if (!inserted) {
            // Подію вже було прийнято й зафіксовано раніше — мовчки ігноруємо повтор
            return IngestResult::DuplicateIgnored;
        }

        return IngestResult::Accepted;
    }
};
```
```ts
import { createHash } from "crypto";

export type CurrencyMicros = bigint; // 1 USD = 1_000_000n micros

export interface UsageEvent {
  eventId: string;
  idempotencyKey: string;
  tenantId: string;
  metricName: string;
  quantity: bigint;
  occurredAt: Date;
  properties?: Record<string, unknown>;
}

export enum IngestStatus {
  Accepted = "ACCEPTED",
  Duplicate = "DUPLICATE_IGNORED",
  Invalid = "INVALID_DATA",
}

export class EventIngestEngine {
  private seenKeys = new Set<string>();

  public ingestEvent(event: UsageEvent): IngestStatus {
    if (!event.tenantId || !event.metricName || event.quantity <= 0n) {
      return IngestStatus.Invalid;
    }

    if (this.seenKeys.has(event.idempotencyKey)) {
      return IngestStatus.Duplicate;
    }

    this.seenKeys.add(event.idempotencyKey);
    return IngestStatus.Accepted;
  }

  public static generateKey(tenantId: string, requestId: string, source: string): string {
    return createHash("sha256")
      .update(`${tenantId}:${requestId}:${source}`)
      .digest("hex");
  }
}
```
:::

## Крок 2: Локальна буферизація та пакетне скидання (Batch Flush Loop)

Відправляти кожну подію споживання в базу даних або віддалений брокер окремим мережевим запитом — класична помилка масштабування. Якщо сервер обробляє 20 000 HTTP-запитів на секунду, 20 000 окремих транзакцій `INSERT` миттєво вичерпають пул з'єднань СУБД та створять колосальне дискове навантаження на журнал випереджального запису (WAL).

Правильне інженерне рішення — локальна безблокувальна буферизація у пам'яті воркера з фоновим скиданням за двома умовами (розмір пакета або таймаут):

1. **Поріг за розміром (Batch Size):** накопичилося `N = 500` подій — буфер негайно скидається одним пакетним `INSERT ... VALUES (...), (...)`.
2. **Поріг за часом (Flush Interval):** минуло `T = 100 мс` — навіть якщо в буфері є лише кілька подій, вони відправляються, щоб мінімізувати затримку надходження даних у білінг.
3. **Штатне завершення (Graceful Shutdown):** під час отримання сигналу `SIGTERM` або `SIGINT` (наприклад, під час планового перерозгортання подів у Kubernetes) воркер миттєво блокує прийом нових запитів, дочікується завершення активних поточних операцій та гарантовано примусово скидає всі залишки буфера в базу даних перед виходом процесу. Якщо процес буде аварійно вбито сигналом `SIGKILL`, непогоджений залишок буфера відновлюється з локального журналу випереджального запису.

:::tabs
```cpp
class BatchEventBuffer {
private:
    std::vector<UsageEvent> buffer_;
    size_t max_batch_size_;
    std::chrono::milliseconds max_delay_;
    std::chrono::steady_clock::time_point last_flush_;

public:
    BatchEventBuffer(size_t max_batch_size, std::chrono::milliseconds max_delay)
        : max_batch_size_(max_batch_size), max_delay_(max_delay), 
          last_flush_(std::chrono::steady_clock::now()) {
        buffer_.reserve(max_batch_size_);
    }

    // Додавання події в локальний буфер; повертає true, якщо потрібен негайний скид
    bool push(UsageEvent event) {
        buffer_.push_back(std::move(event));
        auto now = std::chrono::steady_clock::now();
        if (buffer_.size() >= max_batch_size_ || (now - last_flush_) >= max_delay_) {
            return true;
        }
        return false;
    }

    // Вилучення накопиченого пакета для атомарного запису в базу
    std::vector<UsageEvent> extract_batch() {
        std::vector<UsageEvent> batch;
        batch.swap(buffer_);
        buffer_.reserve(max_batch_size_);
        last_flush_ = std::chrono::steady_clock::now();
        return batch;
    }

    size_t pending_count() const { return buffer_.size(); }
};
```
```ts
export class BatchEventBuffer {
  private buffer: UsageEvent[] = [];
  private maxBatchSize: number;
  private maxDelayMs: number;
  private lastFlushTime: number;

  constructor(maxBatchSize: number = 500, maxDelayMs: number = 100) {
    this.maxBatchSize = maxBatchSize;
    this.maxDelayMs = maxDelayMs;
    this.lastFlushTime = Date.now();
  }

  public push(event: UsageEvent): boolean {
    this.buffer.push(event);
    const now = Date.now();
    if (this.buffer.length >= this.maxBatchSize || now - this.lastFlushTime >= this.maxDelayMs) {
      return true;
    }
    return false;
  }

  public extractBatch(): UsageEvent[] {
    const batch = this.buffer;
    this.buffer = [];
    this.lastFlushTime = Date.now();
    return batch;
  }

  public get pendingCount(): number {
    return this.buffer.length;
  }
}
```
:::

## Крок 3: Шаблон резервування коштів (Hold Pattern)

Коли клієнт ініціює тривалу, пакетну або потенційно дорогу операцію (наприклад, генерацію аудіо, транскрипцію двогодинного відео чи складний пакетний запит до моделі штучного інтелекту), бекенд не може знати фінальну вартість заздалегідь. Кількість згенерованих токенів чи витрачених секунд стає відомою лише після завершення обчислення.

Якщо перевіряти баланс лише після завершення операції, виникає небезпека шахрайства або овердрафту: користувач із $0.05 на рахунку запускає паралельно десять завдань вартістю по $10.00 кожне, заганяючи обліковий запис у глибокий мінус. Якщо ж списувати максимальну суму одразу, клієнт буде переплачувати за завдання, які виконано частково або скасовано.

Розв'язанням є **трифазний шаблон резервування (Hold Pattern)**:

1. **Фаза Hold (Блокування ліміту):** перед передачею завдання у воркер обчислюється максимальна теоретична вартість (`estimated_max_cost`). Якщо доступного балансу клієнта вистачає, ця сума блокується (переводиться в стан `locked_hold`), зменшуючи доступний ліміт для інших паралельних викликів. Створюється об'єкт резервації з унікальним ідентифікатором та строком дії.
2. **Фаза Execute (Виконання):** фоновий процес виконує обчислення, не контактуючи з білінговою базою під час роботи.
3. **Фаза Settle / Release (Фіналізація):**
   - У разі успішного завершення воркер повертає фактичне споживання (`actual_cost`). Система розблоковує повний холд, списує фактичну суму, а невикористану різницю (`reserved - actual`) негайно повертає до вільного балансу клієнта.
   - У разі збою чи помилки сервера холд повністю вивільняється (`release_hold`), повертаючи всі заблоковані кошти без жодних списань.

:::tabs
```cpp
struct Reservation {
    std::string reservation_id;
    std::string tenant_id;
    CurrencyMicros reserved_micros;
    bool is_active;
};

class CreditQuotaManager {
private:
    CurrencyMicros available_balance_micros_;
    CurrencyMicros locked_hold_micros_;

public:
    explicit CreditQuotaManager(CurrencyMicros initial_balance)
        : available_balance_micros_(initial_balance), locked_hold_micros_(0) {}

    // Фаза 1: Резервування ліміту
    std::optional<Reservation> acquire_hold(std::string_view tenant_id, 
                                            std::string_view reservation_id, 
                                            CurrencyMicros estimated_max_cost) {
        if (estimated_max_cost <= 0) return std::nullopt;

        // Перевіряємо чистий доступний баланс з урахуванням інших активних холдів
        if (available_balance_micros_ < estimated_max_cost) {
            return std::nullopt; // Недостатньо коштів для гарантованого старту
        }

        available_balance_micros_ -= estimated_max_cost;
        locked_hold_micros_ += estimated_max_cost;

        return Reservation{
            std::string(reservation_id),
            std::string(tenant_id),
            estimated_max_cost,
            true
        };
    }

    // Фаза 3а: Фіналізація фактичного споживання
    bool settle_hold(Reservation& res, CurrencyMicros actual_cost) {
        if (!res.is_active || actual_cost > res.reserved_micros || actual_cost < 0) {
            return false;
        }

        CurrencyMicros unused_funds = res.reserved_micros - actual_cost;
        locked_hold_micros_ -= res.reserved_micros;
        
        // Повертаємо невикористану різницю назад у доступний баланс
        available_balance_micros_ += unused_funds;
        res.is_active = false;
        return true;
    }

    // Фаза 3б: Скасування та вивільнення в разі помилки
    void release_hold(Reservation& res) {
        if (!res.is_active) return;
        locked_hold_micros_ -= res.reserved_micros;
        available_balance_micros_ += res.reserved_micros;
        res.is_active = false;
    }

    CurrencyMicros get_available_balance() const { return available_balance_micros_; }
};
```
```ts
export interface ActiveReservation {
  reservationId: string;
  tenantId: string;
  reservedMicros: bigint;
  state: "ACTIVE" | "SETTLED" | "RELEASED";
}

export class CreditQuotaManager {
  private availableBalanceMicros: bigint;
  private lockedHoldMicros: bigint = 0n;
  private reservations = new Map<string, ActiveReservation>();

  constructor(initialBalanceMicros: bigint) {
    this.availableBalanceMicros = initialBalanceMicros;
  }

  // Фаза 1: Резервування ліміту
  public acquireHold(tenantId: string, reservationId: string, estimatedMaxCost: bigint): ActiveReservation | null {
    if (estimatedMaxCost <= 0n || this.availableBalanceMicros < estimatedMaxCost) {
      return null; // Недостатній баланс
    }

    this.availableBalanceMicros -= estimatedMaxCost;
    this.lockedHoldMicros += estimatedMaxCost;

    const res: ActiveReservation = {
      reservationId,
      tenantId,
      reservedMicros: estimatedMaxCost,
      state: "ACTIVE",
    };
    this.reservations.set(reservationId, res);
    return res;
  }

  // Фаза 3а: Фіналізація фактичного споживання
  public settleHold(reservationId: string, actualCost: bigint): boolean {
    const res = this.reservations.get(reservationId);
    if (!res || res.state !== "ACTIVE" || actualCost > res.reservedMicros || actualCost < 0n) {
      return false;
    }

    const unusedFunds = res.reservedMicros - actualCost;
    this.lockedHoldMicros -= res.reservedMicros;
    this.availableBalanceMicros += unusedFunds; // повертаємо здачу
    res.state = "SETTLED";
    return true;
  }

  // Фаза 3б: Скасування в разі збою
  public releaseHold(reservationId: string): void {
    const res = this.reservations.get(reservationId);
    if (!res || res.state !== "ACTIVE") return;

    this.lockedHoldMicros -= res.reservedMicros;
    this.availableBalanceMicros += res.reservedMicros;
    res.state = "RELEASED";
  }

  public getAvailableBalance(): bigint {
    return this.availableBalanceMicros;
  }
}
```
:::

## Крок 4: Рушій пошарової тарифікації (Rating Engine)

Отримавши накопичений обсяг споживання за розрахунковий період, рушій тарифікації розбиває обсяг на цінові шари згідно з активним прайс-планом. 

Пошарова модель (Graduated Tiering) гарантує, що знижена ставка застосовується виключно до обсягу, що перевищив порогове значення. Наприклад, якщо перші 1000 одиниць коштують по $0.002, а наступні — по $0.001, то споживання 1500 одиниць розраховується як:
`1000 · 0.002 + 500 · 0.001 = 2.00 + 0.50 = $2.50`.

Усі розрахунки ведуться у фіксованій цілочисельній системі одиниць — мікродоларах (`CurrencyMicros`), де $1.00 відповідає `1 000 000` мікродоларів. Це унеможливлює появу похибок округлення двійкової плаваючої коми IEEE-754:

:::tabs
```cpp
struct PricingTier {
    uint64_t up_to_units;             // UINT64_MAX для останнього рівня (нескінченність)
    CurrencyMicros rate_per_unit_micros;
};

class RatingEngine {
public:
    static CurrencyMicros calculate_graduated_cost(
        uint64_t total_units, 
        const std::vector<PricingTier>& tiers) 
    {
        CurrencyMicros total_cost = 0;
        uint64_t previous_bound = 0;

        for (const auto& tier : tiers) {
            if (total_units <= previous_bound) {
                break;
            }

            uint64_t units_in_tier = 0;
            if (total_units < tier.up_to_units) {
                units_in_tier = total_units - previous_bound;
            } else {
                units_in_tier = tier.up_to_units - previous_bound;
            }

            total_cost += static_cast<CurrencyMicros>(units_in_tier) * tier.rate_per_unit_micros;
            previous_bound = tier.up_to_units;
        }

        return total_cost;
    }
};
```
```ts
export interface PricingTier {
  upToUnits: bigint; // BigInt(Number.MAX_SAFE_INTEGER) для безлімітного верхнього рівня
  ratePerUnitMicros: bigint;
}

export class RatingEngine {
  public static calculateGraduatedCost(totalUnits: bigint, tiers: PricingTier[]): bigint {
    let totalCost: bigint = 0n;
    let previousBound: bigint = 0n;

    for (const tier of tiers) {
      if (totalUnits <= previousBound) {
        break;
      }

      const tierCapacity = tier.upToUnits - previousBound;
      const unitsInThisTier = totalUnits < tier.upToUnits 
        ? totalUnits - previousBound 
        : tierCapacity;

      totalCost += unitsInThisTier * tier.ratePerUnitMicros;
      previousBound = tier.upToUnits;
    }

    return totalCost;
  }
}
```
:::

## Крок 5: Фіксація в реєстрі подвійного запису (Double-Entry Ledger)

Коли послугу фактично спожито й оцінено в грошовому еквіваленті, система фіксує операцію у фінансовому реєстрі. 

Традиційна помилка бекенд-розробників — зберігати баланс як одне числове поле в таблиці користувачів (`accounts.balance`) і змінювати його командою `UPDATE`. За такого підходу неможливо дізнатися, з чого склався поточний баланс, куди зникли кошти в разі аудиторської перевірки, і як відновити стан після збою.

У професійному білінгу баланс рахунку не зберігається як змінне поле. Баланс — це результат згортки (суми) усіх незмінних транзакцій у реєстрі подвійного бухгалтерського запису (Double-Entry General Ledger).

За правилами подвійного запису кожна фінансова операція складається зі збалансованої пари проведень:
1. **Дебет рахунку зобов'язань (`liability:tenant_id`):** зменшує борг компанії перед клієнтом за його передоплачений депозит (проведення з від'ємним знаком суми для пасивного рахунку).
2. **Кредит рахунку доходів (`revenue:api_compute`):** збільшує визнаний дохід платформи за надані послуги (проведення з додатним знаком).

Фундаментальний інваріант реєстру: **сума всіх записів транзакції завжди дорівнює нулю (`∑ amounts == 0`)**. Якщо через баг у коді баланс не зійдеться хоча б на один мікроцент, транзакція відхиляється на рівні бази даних:

:::tabs
```cpp
struct LedgerEntry {
    std::string transaction_id;
    std::string account_id;
    std::string account_type;
    CurrencyMicros amount_micros; // додатне = збільшення, від'ємне = зменшення
    std::string reference_id;
};

class DoubleEntryLedger {
private:
    std::vector<LedgerEntry> entries_;

public:
    bool record_usage_charge(const std::string& transaction_id,
                             const std::string& tenant_id,
                             CurrencyMicros amount_micros,
                             const std::string& event_ref) {
        if (amount_micros <= 0) return false;

        std::string liability_account = "liability:" + tenant_id;
        std::string revenue_account = "revenue:api_compute";

        // Проводка 1: Дебет зобов'язань клієнта (зменшення депозиту на -amount)
        entries_.push_back(LedgerEntry{
            transaction_id,
            liability_account,
            "liability",
            -amount_micros,
            event_ref
        });

        // Проводка 2: Кредит доходів платформи (збільшення виручки на +amount)
        entries_.push_back(LedgerEntry{
            transaction_id,
            revenue_account,
            "revenue",
            amount_micros,
            event_ref
        });

        return true;
    }

    // Розрахунок поточного балансу рахунку через згортку журналу
    CurrencyMicros get_account_balance(const std::string& account_id) const {
        CurrencyMicros balance = 0;
        for (const auto& entry : entries_) {
            if (entry.account_id == account_id) {
                balance += entry.amount_micros;
            }
        }
        return balance;
    }

    // Аудиторська перевірка балансу реєстру: сума всіх транзакцій має дорівнювати 0
    bool verify_audit_invariant() const {
        CurrencyMicros net_sum = 0;
        for (const auto& entry : entries_) {
            net_sum += entry.amount_micros;
        }
        return net_sum == 0;
    }
};
```
```ts
export interface LedgerEntry {
  transactionId: string;
  accountId: string;
  accountType: "asset" | "liability" | "revenue" | "expense";
  amountMicros: bigint;
  referenceId: string;
  createdAt: Date;
}

export class DoubleEntryLedger {
  private entries: LedgerEntry[] = [];

  public recordUsageCharge(
    transactionId: string,
    tenantId: string,
    amountMicros: bigint,
    eventRef: string
  ): boolean {
    if (amountMicros <= 0n) return false;

    const liabilityAccount = `liability:${tenantId}`;
    const revenueAccount = "revenue:api_compute";

    // 1. Дебет рахунку депозиту клієнта (-amount)
    this.entries.push({
      transactionId,
      accountId: liabilityAccount,
      accountType: "liability",
      amountMicros: -amountMicros,
      referenceId: eventRef,
      createdAt: new Date(),
    });

    // 2. Кредит доходу платформи (+amount)
    this.entries.push({
      transactionId,
      accountId: revenueAccount,
      accountType: "revenue",
      amountMicros: amountMicros,
      referenceId: eventRef,
      createdAt: new Date(),
    });

    return true;
  }

  public getAccountBalance(accountId: string): bigint {
    return this.entries
      .filter((e) => e.accountId === accountId)
      .reduce((sum, e) => sum + e.amountMicros, 0n);
  }

  public verifyAuditInvariant(): boolean {
    const totalSum = this.entries.reduce((sum, e) => sum + e.amountMicros, 0n);
    return totalSum === 0n;
  }
}
```
:::

## Інтеграційний сценарій: повний цикл обробки

Простежимо наскрізний потік даних під час обробки одного реального клієнтського виклику:

1. **Крок А:** Клієнт `tenant_alpha_42` ініціює важкий запит. Система квот перевіряє доступний баланс ($10.00) і встановлює холд на $5.00 (`acquire_hold`). Вільний залишок стає $5.00.
2. **Крок Б:** Воркер виконує генерацію і додає подію споживання 1500 токенів у локальний буфер `BatchEventBuffer`.
3. **Крок В:** Пакет подій скидається та проходить дедуплікацію в `EventIngestEngine` за унікальним відбитком.
4. **Крок Г:** Рушій тарифікації розраховує пошарову вартість: `1000 * $0.002 + 500 * $0.001 = $2.50`.
5. **Крок Ґ:** Менеджер квот фіналізує холд (`settle_hold`): списує $2.50, а невикористані $2.50 повертає в доступний баланс клієнта (новий доступний залишок стає $7.50).
6. **Крок Д:** Реєстр подвійного запису зберігає збалансовану пару проводок (`record_usage_charge`), збільшуючи виручку платформи на $2.50 та зменшуючи зобов'язання перед клієнтом на $2.50.

:::tabs
```cpp
int main() {
    // 1. Ініціалізація: клієнт має депозит $10.00 (10 000 000 мікродоларів)
    CreditQuotaManager quota(10'000'000);
    DoubleEntryLedger ledger;
    EventIngestEngine ingest;
    BatchEventBuffer buffer(100, std::chrono::milliseconds(50));

    std::string tenant = "tenant_alpha_42";

    // Тарифна сітка: перші 1000 токенів по $0.002, понад 1000 по $0.001
    std::vector<PricingTier> tiers = {
        {1000, 2000},                 // $0.002 за одиницю (2000 micros)
        {UINT64_MAX, 1000}            // $0.001 за одиницю (1000 micros)
    };

    // Крок А: Запит на виконання важкого запиту (Hold $5.00)
    auto hold = quota.acquire_hold(tenant, "hold_req_9981", 5'000'000);
    if (!hold) {
        std::cerr << "Помилка: Недостатньо коштів на балансі!" << std::endl;
        return 1;
    }
    std::cout << "Холд успішно встановлено на $5.00. Доступний залишок: $" 
              << (quota.get_available_balance() / 1'000'000.0) << std::endl;

    // Крок Б: Виконання роботи та буферизація події споживання
    UsageEvent event{
        "evt_1001",
        "hash_tenant_alpha_42_req_9981",
        tenant,
        "llm_tokens",
        1500,
        std::chrono::system_clock::now()
    };
    buffer.push(event);

    // Крок В: Скидання пакета та прийом у ядро
    auto batch = buffer.extract_batch();
    for (const auto& ev : batch) {
        auto status = ingest.ingest_event(ev);
        if (status != IngestResult::Accepted) {
            quota.release_hold(*hold);
            return 1;
        }
    }

    // Крок Г: Тарифікація ($2.50)
    CurrencyMicros final_cost = RatingEngine::calculate_graduated_cost(event.quantity, tiers);

    // Крок Ґ: Завершення холду ($2.50 списано, $2.50 повернено в доступні)
    quota.settle_hold(*hold, final_cost);

    // Крок Д: Фіксація в незмінному реєстрі
    ledger.record_usage_charge("tx_88112", tenant, final_cost, event.event_id);

    std::cout << "Операцію завершено." << std::endl;
    std::cout << "Фактична вартість: $" << (final_cost / 1'000'000.0) << std::endl;
    std::cout << "Фінальний доступний баланс: $" << (quota.get_available_balance() / 1'000'000.0) << std::endl;
    std::cout << "Баланс реєстру зобов'язань: $" 
              << (ledger.get_account_balance("liability:" + tenant) / 1'000'000.0) << std::endl;
    std::cout << "Аудит реєстру збігається: " << (ledger.verify_audit_invariant() ? "ТАК" : "НІ") << std::endl;

    return 0;
}
```
```ts
function runSimulation(): void {
  const quota = new CreditQuotaManager(10_000_000n); // $10.00 депозит
  const ledger = new DoubleEntryLedger();
  const ingest = new EventIngestEngine();
  const buffer = new BatchEventBuffer(100, 50);

  const tenant = "tenant_alpha_42";
  const tiers: PricingTier[] = [
    { upToUnits: 1000n, ratePerUnitMicros: 2000n }, // $0.002
    { upToUnits: BigInt(Number.MAX_SAFE_INTEGER), ratePerUnitMicros: 1000n }, // $0.001
  ];

  // Крок А: Холд $5.00
  const hold = quota.acquireHold(tenant, "hold_req_9981", 5_000_000n);
  if (!hold) {
    throw new Error("Недостатньо коштів на балансі");
  }

  // Крок Б: Буферизація події
  const eventKey = EventIngestEngine.generateKey(tenant, "req_9981", "worker_node_1");
  const event: UsageEvent = {
    eventId: "evt_1001",
    idempotencyKey: eventKey,
    tenantId: tenant,
    metricName: "llm_tokens",
    quantity: 1500n,
    occurredAt: new Date(),
  };
  buffer.push(event);

  // Крок В: Пакетний скид та дедуплікація
  const batch = buffer.extractBatch();
  for (const ev of batch) {
    const status = ingest.ingestEvent(ev);
    if (status !== IngestStatus.Accepted) {
      quota.releaseHold(hold.reservationId);
      return;
    }
  }

  // Крок Г: Тарифікація (1000*2000 + 500*1000 = 2_500_000n = $2.50)
  const actualCost = RatingEngine.calculateGraduatedCost(event.quantity, tiers);

  // Крок Ґ: Завершення холду
  quota.settleHold(hold.reservationId, actualCost);

  // Крок Д: Подвійний запис у реєстр
  ledger.recordUsageCharge("tx_88112", tenant, actualCost, event.eventId);

  console.log(`Баланс клієнта: $${Number(quota.getAvailableBalance()) / 1_000_000}`);
  console.log(`Аудит реєстру валідний: ${ledger.verifyAuditInvariant()}`);
}

runSimulation();
```
:::

## Звірка, аудиторський баланс та запізнілі події

У реальній фінансовій системі розробник стикається з трьома критичними ситуаціями, коли проста схема обробки натикається на вимоги бухгалтерського аудиту:

### 1. Щоденне аудиторське зведення (Trial Balance)

Щоб переконатися, що жодна транзакція не була пошкоджена або частково записана через збій диска чи баг у коді, щоночі запускається фонова процедура аудиторської звірки. Вона перевіряє два ключові інваріанти:

```sql
-- Перевірка 1: Нульовий баланс кожної окремої транзакції
SELECT transaction_id, SUM(amount_micros) AS discrepancy
FROM ledger_entries
GROUP BY transaction_id
HAVING SUM(amount_micros) != 0;
```

Якщо цей запит повертає хоча б один рядок — у системі стався критичний інцидент цілісності даних. Другий інваріант перевіряє, що сумарна зміна рахунків зобов'язань перед усіма клієнтами точно дорівнює визнаному доходу плюс сума невикористаних депозитів:

```sql
-- Перевірка 2: Глобальний баланс активів, зобов'язань і доходів
SELECT 
    account_type,
    SUM(amount_micros) AS total_balance
FROM ledger_entries
GROUP BY account_type;
```

Ці звірки дають компанії можливість гарантувати фінансову відповідність міжнародним стандартам GAAP та SOX, оскільки будь-яке несанкціоноване втручання чи програмний збій негайно виявляються на математичному рівні балансу.

### 2. Механізм сторнування та коригувань (Compensating Entries)

Якщо клієнту було помилково нараховано плату за збійний виклик або служба підтримки схвалила повернення коштів (Refund), фінансовий запис ніколи не виправляється через `UPDATE` чи `DELETE`. Пряма модифікація історичних рядків позбавляє реєстр юридичної сили перед податковими органами та аудиторами (SOX/GAAP compliance).

Замість цього створюється **компенсаційна транзакція (Reversal Transaction)**:
- **Кредит зобов'язань клієнта (`liability:tenant_id`):** збільшує депозит клієнта на суму повернення (+amount).
- **Дебет доходів платформи (`revenue:api_compute`):** зменшує виручку платформи (-amount).

Історія залишається абсолютно прозорою: видно і первинне помилкове списання, і наступне коригувальне нарахування.

### 3. Обробка запізнілих подій (Late-Arriving Events)

У розподілених системах клієнти мобільних застосунків, IoT-пристрої або ізольовані регіональні кластери можуть втратити зв'язок із центральним сервером на години чи дні. Коли зв'язок відновлюється, у конвеєр надходить пакет подій із мітками `occurred_at`, які вказують на минулий тиждень, за який білінговий період уже було закрито й виставлено фінальний інвойс.

Конвеєр розділяє дві мітки часу:
- **Час події (`occurred_at`):** використовується рушієм тарифікації для визначення того тарифного плану й цін, які діяли *саме на момент здійснення операції*.
- **Час проведення (`created_at = now()`):** фіксує транзакцію у фінансовому реєстрі *поточним моментом часу*.

Завдяки цьому вже сформовані та оплачені інвойси минулого періоду залишаються незмінними, а запізніла плата автоматично переноситься як коригування (Adjustment / Overage) у наступний відкритий розрахунковий період.

## Інженерні висновки та пастки впровадження

Під час експлуатації конвеєра обліку у високонавантаженому розподіленому середовищі виникають чотири критичні інженерні пастки:

1. **Строк життя та очищення ключів дедуплікації (TTL Window):**
   Таблиця `usage_events` або індекс ідемпотентності не повинні рости нескінченно. Оскільки клієнтські повтори трапляються впродовж секунд або хвилин після збою мережі, для ключів встановлюється вікно дедуплікації (зазвичай 24–72 години). Старі записи переміщуються у партиційований холодний архів (ClickHouse або S3 Parquet), а первинний унікальний індекс оперативно очищається.

2. **Захист від витоку пам'яті та коштів через завислі холди (Orphaned Holds):**
   Якщо воркер зазнав аварійного відключення (`OOMKilled`, збій заліза чи деплой нового коду) після взяття холду, але до виклику `settle` чи `release`, заблоковані кошти можуть назавжди зависнути, блокуючи клієнтові доступ до сервісу. Фоновий процес-прибиральник (Janitor Worker) кожні кілька хвилин сканує таблицю `credit_reservations` і автоматично вивільняє будь-які холди зі станом `active`, у яких `expires_at < now()`.

3. **Стійкість до аварій та гарантія At-Least-Once доставки:**
   Локальний буфер воркера тримає події в оперативній пам'яті. Щоб уникнути втрати даних під час раптового вимкнення живлення сервера, висококритичні системи записують подію у локальний журнал випереджального запису (Embedded RocksDB або SQLite WAL на NVMe-диску) перед підтвердженням завершення HTTP-запиту клієнту.

4. **Розділення сховищ для аналітики та фінансового аудиту:**
   Сирий потік подій (мільярди рядків на місяць) ефективно зберігати у колонкових базах (ClickHouse), де компресія досягає 90% завдяки однотипним міткам часу та числовим метрикам. Фінансовий же реєстр `ledger_entries` зберігається в транзакційній реляційній базі даних (PostgreSQL) із максимальними гарантіями цілісності ACID та синхронною реплікацією.
