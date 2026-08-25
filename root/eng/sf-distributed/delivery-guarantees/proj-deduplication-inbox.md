# ⚙️ Реалізація надійного споживача: ковзне вікно дедуплікації та Transactional Inbox

<preknowlist>
- [Ідемпотентність](topic:sf-distributed/idempotency) — властивість операції давати однаковий кінцевий результат незалежно від кількості повторних викликів.
- [Transactional outbox](topic:sf-distributed/outbox-pattern) — патерн атомарного збереження стану бізнес-сутності та повідомлення в одній локальній транзакції бази даних.
- [Вхідна скринька (inbox)](topic:sf-distributed/inbox-pattern) — збереження вхідних ідентифікаторів повідомлень для гарантії дедуплікації на боці споживача.
</preknowlist>

Коли черга повідомлень або журнал подій працює в режимі *at-least-once*, споживач (*consumer*) гарантовано отримуватиме дублікати повідомлень. Це відбувається щоразу, коли робітник падає після обробки повідомлення, але до відправки підтвердження (ACK), або коли мережева затримка змушує брокер перепризначити повідомлення іншому обробнику. Якщо споживач виконує неідемпотентну бізнес-дію (наприклад, списання коштів або резервування товару), наївний код призведе до подвійного списання грошей та розриву фінансового балансу.

Цей проєкт демонструє повноцінну, стійку до збоїв реалізацію споживача на основі патерну **Transactional Inbox** у поєднанні з **дворівневим ковзним вікном дедуплікації** (швидкий фільтр в оперативній пам'яті + надійне транзакційне сховище).

## Архітектурний дизайн та багаторівневий захист

Щоб перетворити потік із повторами на надійну семантику «рівно один результат» (*effectively-once*), споживач не може покладатися на одне лише сховище чи один лише локальний кеш. Якщо виконувати перевірку виключно в реляційній базі даних, кожен дублікат під час аварійного шторму повторів (*retry storm*) створюватиме важкий дисковий запит, блокуватиме таблиці та перевантажуватиме пул з'єднань. Якщо ж зберігати ключі лише в оперативній пам'яті процесу, перезапуск робітника зітре історію, і перший же повтор призведе до повторного виконання бізнес-дії.

Стійка промислова архітектура будується як багаторівневий конвеєр:

1. **Глобально унікальний ключ повідомлення:** кожне вхідне повідомлення містить детермінований ідентифікатор `idempotency_key` або `message_id` (наприклад, комбінацію сутності та операції `pay_order_84920_attempt_1`).
2. **Рівень L1 (Швидкий фільтр в оперативній пам'яті):** ковзне часове вікно (*sliding time-window*) з обмеженим часом життя (TTL), що відсікає високочастотні дублікати (які надходять протягом кількох секунд або хвилин після оригіналу) взагалі без звернення до бази даних.
3. **Рівень L2 (Транзакційний Inbox у реляційній БД):** персистентна таблиця `inbox_messages` з унікальним індексом (`UNIQUE INDEX`), яка оновлюється в межах тієї самої локальної ACID-транзакції, що й бізнес-мутація балансу.
4. **Атомарний компроміс стану:** зміна бізнес-даних і збереження ключа в інбоксі виконуються як неподільна операція. Або обидва записи надійно зафіксовані на диску, або жоден.
5. **Послідовність коміту зміщень:** відправка підтвердження брокеру (`ACK` або `commitSync`) відбувається **суворо після** успішного завершення транзакції бази даних.

## Реалізація двома мовами: C та C++

Нижче наведено повну робочу реалізацію споживача. Варіант мовою C використовує структуроване ручне керування пам'яттю, фіксовані таблиці та явні коди помилок. Варіант мовою C++ реалізує ідіоматичний підхід: керування життєвим циклом транзакцій через RAII, безпечні стандартні контейнери, роботу з `std::string_view` без зайвих копіювань та сучасний тип результату `std::expected`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>

#define MAX_MSG_ID_LEN 64
#define CACHE_CAPACITY 1024

/* Типи результатів обробки */
typedef enum {
    CONSUME_OK_PROCESSED,    /* Повідомлення нове, успішно оброблено */
    CONSUME_OK_DUPLICATE,    /* Повідомлення дублікатне, пропущено без помилки */
    CONSUME_ERR_TRANSACTION  /* Помилка сховища / бази даних */
} ConsumeStatus;

/* Структура повідомлення */
typedef struct {
    char id[MAX_MSG_ID_LEN];
    long account_id;
    double amount;
} PaymentMessage;

/* Запис ковзного вікна дедуплікації в оперативній пам'яті (L1) */
typedef struct {
    char id[MAX_MSG_ID_LEN];
    time_t seen_at;
    bool in_use;
} CacheEntry;

/* Імітація бази даних споживача (L2) */
typedef struct {
    double balance;
    char processed_inbox[CACHE_CAPACITY][MAX_MSG_ID_LEN];
    size_t inbox_count;
    bool in_transaction;
} MockDatabase;

/* Стан надійного споживача */
typedef struct {
    MockDatabase db;
    CacheEntry l1_cache[CACHE_CAPACITY];
    time_t window_ttl_seconds;
} ReliableConsumer;

/* Ініціалізація споживача */
void consumer_init(ReliableConsumer *c, double initial_balance, time_t ttl_sec) {
    memset(c, 0, sizeof(ReliableConsumer));
    c->db.balance = initial_balance;
    c->window_ttl_seconds = ttl_sec;
}

/* Перевірка швидкого кешу в пам'яті */
static bool l1_cache_contains(ReliableConsumer *c, const char *msg_id, time_t now) {
    for (size_t i = 0; i < CACHE_CAPACITY; ++i) {
        if (c->l1_cache[i].in_use) {
            if (now - c->l1_cache[i].seen_at > c->window_ttl_seconds) {
                c->l1_cache[i].in_use = false; /* Протухлий запис */
                continue;
            }
            if (strncmp(c->l1_cache[i].id, msg_id, MAX_MSG_ID_LEN) == 0) {
                return true;
            }
        }
    }
    return false;
}

/* Додавання запису до кешу пам'яті */
static void l1_cache_insert(ReliableConsumer *c, const char *msg_id, time_t now) {
    size_t victim_idx = 0;
    time_t oldest_time = now + 1;

    for (size_t i = 0; i < CACHE_CAPACITY; ++i) {
        if (!c->l1_cache[i].in_use) {
            victim_idx = i;
            break;
        }
        if (c->l1_cache[i].seen_at < oldest_time) {
            oldest_time = c->l1_cache[i].seen_at;
            victim_idx = i;
        }
    }

    strncpy(c->l1_cache[victim_idx].id, msg_id, MAX_MSG_ID_LEN - 1);
    c->l1_cache[victim_idx].id[MAX_MSG_ID_LEN - 1] = '\0';
    c->l1_cache[victim_idx].seen_at = now;
    c->l1_cache[victim_idx].in_use = true;
}

/* Атомарна обробка в межах локальної транзакції */
ConsumeStatus consumer_process_message(ReliableConsumer *c, const PaymentMessage *msg) {
    time_t now = time(NULL);

    /* Крок 1: Швидка перевірка в кеші L1 */
    if (l1_cache_contains(c, msg->id, now)) {
        return CONSUME_OK_DUPLICATE;
    }

    /* Крок 2: Початок транзакції БД */
    c->db.in_transaction = true;

    /* Крок 3: Перевірка та вставка в таблицю Inbox БД (L2) */
    for (size_t i = 0; i < c->db.inbox_count; ++i) {
        if (strncmp(c->db.processed_inbox[i], msg->id, MAX_MSG_ID_LEN) == 0) {
            c->db.in_transaction = false; /* Відкат транзакції */
            l1_cache_insert(c, msg->id, now); /* Оновлюємо L1 кеш */
            return CONSUME_OK_DUPLICATE;
        }
    }

    /* Крок 4: Виконання бізнес-мутації */
    c->db.balance += msg->amount;

    /* Фіксація ключа в Inbox */
    if (c->db.inbox_count < CACHE_CAPACITY) {
        strncpy(c->db.processed_inbox[c->db.inbox_count], msg->id, MAX_MSG_ID_LEN - 1);
        c->db.processed_inbox[c->db.inbox_count][MAX_MSG_ID_LEN - 1] = '\0';
        c->db.inbox_count++;
    }

    /* Крок 5: Коміт транзакції БД */
    c->db.in_transaction = false;

    /* Крок 6: Оновлення L1 кешу після успіху */
    l1_cache_insert(c, msg->id, now);

    return CONSUME_OK_PROCESSED;
}

int main(void) {
    ReliableConsumer consumer;
    consumer_init(&consumer, 1000.0, 300); /* Початковий баланс 1000 грн, TTL 300 с */

    PaymentMessage msg1 = {"tx_9981_order_44", 101, 250.0};
    PaymentMessage duplicate = {"tx_9981_order_44", 101, 250.0};
    PaymentMessage msg2 = {"tx_9982_order_45", 101, 100.0};

    printf("Початковий баланс: %.2f грн\n", consumer.db.balance);

    /* Перша доставка msg1 */
    ConsumeStatus st1 = consumer_process_message(&consumer, &msg1);
    printf("Спроба 1 (msg1): %s, Баланс: %.2f грн\n",
           st1 == CONSUME_OK_PROCESSED ? "ОБРОБЛЕНО" : "ДУБЛІКАТ", consumer.db.balance);

    /* Мережевий повтор msg1 через збій ACK */
    ConsumeStatus st_dup = consumer_process_message(&consumer, &duplicate);
    printf("Спроба 2 (повтор msg1): %s, Баланс: %.2f грн\n",
           st_dup == CONSUME_OK_PROCESSED ? "ОБРОБЛЕНО" : "ДУБЛІКАТ (відсічено)", consumer.db.balance);

    /* Нове повідомлення msg2 */
    ConsumeStatus st2 = consumer_process_message(&consumer, &msg2);
    printf("Спроба 3 (msg2): %s, Баланс: %.2f грн\n",
           st2 == CONSUME_OK_PROCESSED ? "ОБРОБЛЕНО" : "ДУБЛІКАТ", consumer.db.balance);

    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_set>
#include <unordered_map>
#include <chrono>
#include <memory>
#include <expected>
#include <stdexcept>

// DTO вхідного повідомлення
struct PaymentMessage {
    std::string id;
    int64_t account_id;
    double amount;
};

// Можливі стани результату обробки
enum class ProcessingResult {
    Processed,
    DuplicateSkipped
};

// RAII обгортка для локальної транзакції бази даних
class DatabaseTransaction {
public:
    explicit DatabaseTransaction(bool &in_tx_flag) : in_tx_(in_tx_flag), committed_(false) {
        if (in_tx_) {
            throw std::runtime_error("Вкладені транзакції не підтримуються");
        }
        in_tx_ = true;
    }

    void commit() {
        committed_ = true;
    }

    ~DatabaseTransaction() noexcept {
        in_tx_ = false; // Якщо не було явного commit(), відбувається відкат
    }

    DatabaseTransaction(const DatabaseTransaction &) = delete;
    DatabaseTransaction &operator=(const DatabaseTransaction &) = delete;

private:
    bool &in_tx_;
    bool committed_;
};

// Імітація персистентного сховища з підтримкою транзакцій (L2)
class StorageEngine {
public:
    explicit StorageEngine(double initial_balance) : balance_(initial_balance), in_tx_(false) {}

    [[nodiscard]] double balance() const noexcept {
        return balance_;
    }

    [[nodiscard]] bool contains_inbox(std::string_view msg_id) const {
        return inbox_table_.contains(std::string(msg_id));
    }

    void insert_inbox(std::string_view msg_id) {
        inbox_table_.insert(std::string(msg_id));
    }

    void apply_balance_mutation(double delta) {
        balance_ += delta;
    }

    [[nodiscard]] DatabaseTransaction begin_transaction() {
        return DatabaseTransaction(in_tx_);
    }

private:
    double balance_;
    bool in_tx_;
    std::unordered_set<std::string> inbox_table_;
};

// Ковзне вікно дедуплікації в оперативній пам'яті (L1)
class SlidingWindowCache {
public:
    explicit SlidingWindowCache(std::chrono::seconds ttl) : ttl_(ttl) {}

    [[nodiscard]] bool contains(std::string_view key, std::chrono::steady_clock::time_point now) {
        cleanup(now);
        return cache_.contains(std::string(key));
    }

    void insert(std::string_view key, std::chrono::steady_clock::time_point now) {
        cache_[std::string(key)] = now;
    }

private:
    void cleanup(std::chrono::steady_clock::time_point now) {
        for (auto it = cache_.begin(); it != cache_.end();) {
            if (now - it->second > ttl_) {
                it = cache_.erase(it);
            } else {
                ++it;
            }
        }
    }

    std::chrono::seconds ttl_;
    std::unordered_map<std::string, std::chrono::steady_clock::time_point> cache_;
};

// Стійкий споживач з Transactional Inbox
class ReliableConsumer {
public:
    ReliableConsumer(double initial_balance, std::chrono::seconds cache_ttl)
        : storage_(initial_balance), l1_cache_(cache_ttl) {}

    std::expected<ProcessingResult, std::string> process_message(const PaymentMessage &msg) {
        const auto now = std::chrono::steady_clock::now();

        // 1. Швидка перевірка в L1 кеші
        if (l1_cache_.contains(msg.id, now)) {
            return ProcessingResult::DuplicateSkipped;
        }

        try {
            // 2. Старт локальної ACID транзакції
            auto tx = storage_.begin_transaction();

            // 3. Перевірка дублювання в L2 Inbox таблиці
            if (storage_.contains_inbox(msg.id)) {
                l1_cache_.insert(msg.id, now);
                return ProcessingResult::DuplicateSkipped;
            }

            // 4. Бізнес-дія: нарахування/списання балансу
            storage_.apply_balance_mutation(msg.amount);

            // 5. Запис ключа в Inbox у межах тієї ж транзакції
            storage_.insert_inbox(msg.id);

            // 6. Фіксація транзакції
            tx.commit();

            // 7. Оновлення L1 фільтра після успішної фіксації
            l1_cache_.insert(msg.id, now);

            return ProcessingResult::Processed;
        } catch (const std::exception &ex) {
            return std::unexpected(std::string("Помилка обробки транзакції: ") + ex.what());
        }
    }

    [[nodiscard]] double current_balance() const noexcept {
        return storage_.balance();
    }

private:
    StorageEngine storage_;
    SlidingWindowCache l1_cache_;
};

int main() {
    using namespace std::chrono_literals;

    ReliableConsumer consumer(1000.0, 300s); // 1000 грн початковий баланс, 300с TTL

    const PaymentMessage msg1{"tx_9981_order_44", 101, 250.0};
    const PaymentMessage duplicate{"tx_9981_order_44", 101, 250.0};
    const PaymentMessage msg2{"tx_9982_order_45", 101, 100.0};

    std::cout << "Початковий баланс: " << consumer.current_balance() << " грн\n";

    // Спроба 1: оригінальне повідомлення
    auto res1 = consumer.process_message(msg1);
    if (res1) {
        std::cout << "Спроба 1 (msg1): "
                  << (*res1 == ProcessingResult::Processed ? "ОБРОБЛЕНО" : "ДУБЛІКАТ")
                  << ", Баланс: " << consumer.current_balance() << " грн\n";
    }

    // Спроба 2: мережевий дублікат
    auto res_dup = consumer.process_message(duplicate);
    if (res_dup) {
        std::cout << "Спроба 2 (повтор msg1): "
                  << (*res_dup == ProcessingResult::Processed ? "ОБРОБЛЕНО" : "ДУБЛІКАТ (відсічено)")
                  << ", Баланс: " << consumer.current_balance() << " грн\n";
    }

    // Спроба 3: нове повідомлення
    auto res2 = consumer.process_message(msg2);
    if (res2) {
        std::cout << "Спроба 3 (msg2): "
                  << (*res2 == ProcessingResult::Processed ? "ОБРОБЛЕНО" : "ДУБЛІКАТ")
                  << ", Баланс: " << consumer.current_balance() << " грн\n";
    }

    return 0;
}
```
:::

## Детальний розбір реалізації та управління ресурсами

Погляньмо на те, як реалізовано ключові механізми в коді та чому вони побудовані саме так.

### Ручне керування пам'яттю та фіксовані структури в C

У C-реалізації свідомо використано статично виділені буфери `CacheEntry` та таблиці фіксованого розміру `MockDatabase`.

Це дає три суттєві інженерні переваги:
1. **Відсутність динамічної алокації (`malloc`/`free`) на гарячому шляху:** під час обробки 100 000 повідомлень за секунду фрагментація купи (*heap fragmentation*) та накладні витрати на виклики системного алокатора здатні спричинити непередбачувані затримки.
2. **Детерміноване витіснення жертв (*Victim Eviction*):** функція `l1_cache_insert` шукає або вільний слот, або найстаріший за часом запис (`oldest_time`). Це гарантує, що пам'ять процесу ніколи не перевищить виділений бюджет, навіть під час нескінченного потоку нових ключів.
3. **Локальність кешу процесора (L1/L2 CPU Cache):** суцільний масив структур `CacheEntry` розташований у неперервному блоці віртуальної пам'яті, що мінімізує промахи ліній кешу процесора (*cache misses*) під час лінійного сканування.

### Ідіоматичні патерни в C++

C++ реалізація демонструє сучасні підходи стандарту C++20/C++23:

- **RAII транзакцій (`DatabaseTransaction`):** деструктор класу автоматично скидає прапорець транзакції `in_tx_ = false`, якщо обробка завершилася винятком до виклику `commit()`. Це унеможливлює зависання незавершених транзакцій у системі.
- **Тип `std::expected` замість винятків:** для передбачуваних бізнес-розгалужень (наприклад, дублікатне повідомлення чи системна помилка) функція повертає `std::expected<ProcessingResult, std::string>`. Це дозволяє уникнути важких накладних витрат на розгортання стека (*stack unwinding*), зберігаючи строгу типізацію помилок.
- **Передача `std::string_view`:** рядкові ідентифікатори передаються за значенням як легковажні пари «вказівник + довжина» (16 байтів на 64-бітній платформі), що усуває зайве копіювання рядків при перевірці в кешах.

## Реляційна схема бази даних та індекси

Розглянемо, як ця логіка проєктується на реальні виробничі сховища даних (PostgreSQL, MySQL або CockroachDB).

### Реляційна схема таблиці Inbox

Для ефективної роботи таблиці `inbox_messages` у виробничій системі недостатньо простого первинного ключа. Потрібно враховувати як швидкість перевірки, так і вартість очищення застарілих даних.

```sql
CREATE TABLE inbox_messages (
    id VARCHAR(64) NOT NULL,
    consumer_group VARCHAR(64) NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    response_payload JSONB NULL,
    PRIMARY KEY (consumer_group, id)
) PARTITION BY RANGE (processed_at);
```

Чому обрано саме таку структуру:
- **Складений первинний ключ `(consumer_group, id)`:** дозволяє різним незалежним мікросервісам (наприклад, білінгу та складському сервісу) використовувати власні ідентифікатори обробки одного й того самого вхідного повідомлення без колізій.
- **Поле `response_payload`:** зберігає серіалізований результат первинної обробки. Якщо зовнішній клієнт виконує синхронний повторний RPC/HTTP-запит, сервіс не просто відхиляє дублікат, а повертає збережений раніше результат (наприклад, статус замовлення та квитанцію).
- **Секціонування за часом (`PARTITION BY RANGE`):** розбиває таблицю на щоденні або щотижневі секції.

### Очищення застарілих записів: DROP PARTITION замість DELETE

Класична помилка при експлуатації таблиць дедуплікації — періодичний запуск фонового видалення рядків:

```sql
-- ПОГАНО: створює гігантське навантаження на WAL і фрагментацію B-Tree індексів
DELETE FROM inbox_messages WHERE processed_at < NOW() - INTERVAL '14 days';
```

Масовий `DELETE` мільйонів рядків спричиняє роздування таблиць (*table bloat*), викликає блокування автоочищення (*autovacuum*) та навантажує дискову підсистему.

**Правильний підхід:**
Створення щоденних партицій. Коли вікно давності виходить за межі 14 днів, фоновий процес виконує миттєву команду скидання секції:

```sql
-- ДОБРЕ: миттєве звільнення файлового простору без блокувань
DROP TABLE inbox_messages_y2026_m08_d01;
```

Операція `DROP TABLE` виконується за кілька мілісекунд, не пише в журнал транзакцій змісту рядків і миттєво повертає дисковий простір операційній системі.

## Багатопотокова конкурентність та шардинг

У високонавантажених сервісах споживач зазвичай працює не в один потік, а як пул із `M` паралельних потоків-робітників.

Якщо кілька потоків паралельно вичитують повідомлення з черги, виникає ризик блокування транзакцій на рівні рядків бази даних:

1. **Маршрутизація за ключем (Key-based Partitioning):**
   Усі повідомлення, що стосуються одного облікового запису (`account_id`), обов'язково публікуються в одну й ту саму партицію брокера за хешем ключа:
   ```
   partition = hash(account_id) % num_partitions
   ```
   Це гарантує, що повідомлення одного акаунта завжди обробляються суворо одним і тим самим потоком послідовно, повністю усуваючи конкурентні блокування в базі даних.

2. **Локальні черги потоків усередині процесу:**
   Якщо споживач вичитує дані батчами з однієї партиції, він розподіляє повідомлення між внутрішніми чергами потоків за хешем `account_id`, зберігаючи послідовність операцій для кожного клієнта окремо.

## Реалізація фонового диспетчера Transactional Outbox (Outbox Relay)

Коли обробник завершив транзакцію та зберіг подію в таблиці `outbox_events`, її необхідно надійно передати у вихідний топік брокера (Kafka або RabbitMQ).

Для цього застосовують два промислові патерни:

### 1. Патерн опитування з блокуванням SKIP LOCKED
Фоновий процес виконує вибірку батчу невідправлених подій, блокуючи лише вільні рядки, щоб кілька паралельних диспетчерів не конкурували за одні й ті самі записи:

```sql
BEGIN;
SELECT id, aggregate_id, event_type, payload
FROM outbox_events
WHERE status = 'PENDING'
ORDER BY created_at ASC
LIMIT 100
FOR UPDATE SKIP LOCKED;

-- Після успішної публікації в Kafka:
UPDATE outbox_events
SET status = 'PUBLISHED', published_at = NOW()
WHERE id IN (...);
COMMIT;
```

Використання `SKIP LOCKED` усуває взаємні блокування (*deadlocks*) між робітниками та дозволяє горизонтально масштабувати диспетчери вихідних повідомлень.

### 2. Захоплення змін журналу (Change Data Capture, CDC)
Для надвисоких навантажень (понад 100 000 подій/с) опитування бази даних через SQL стає надто дорогим. Замість цього використовують коннектори рівня Debezium, які підключаються безпосередньо до бінарного журналу реплікації бази даних (PostgreSQL `pgoutput` або MySQL `binlog`).

Debezium зчитує вставки в таблицю `outbox_events` із WAL-файлу без виконання жодного SQL-запиту до рушія таблиць і гарантовано ретранслює їх у Kafka з власним циклом ідемпотентних повторів.

## Аналіз крайових випадків та типові пастки

Під час експлуатації цієї схеми у високонавантажених розподілених середовищах виникають чотири критичні сценарії відмови, які вимагають окремого аналізу.

### Пастка 1: Збій між транзакцією БД та відправкою ACK брокеру

Припустимо, транзакція БД успішно зафіксувала `COMMIT`, гроші списано, а `message_id` записано в `inbox_messages`. Проте за мікросекунду до відправки `ACK` брокеру процес споживача вбиває операційна система (`OOM Killer` через нестачу пам'яті або раптове знеструмлення машини).

**Що відбувається:**
Брокер черги повідомлень фіксує таймаут видимості (*visibility timeout*) або обрив TCP-сесії й передає те саме повідомлення іншій копії споживача. Новий споживач отримує повідомлення, відкриває транзакцію й запитує базу даних:

```sql
SELECT 1 FROM inbox_messages WHERE consumer_group = 'billing' AND id = 'tx_9981';
```

База даних повертає `true` (запис існує). Споживач **не виконує повторного списання балансу**, негайно фіксує успіх і відправляє `ACK` брокеру. Система автоматично повернулася до узгодженого стану без ручного втручання адміністратора.

### Пастка 2: Конкурентна паралельна доставка двох копій

Якщо два однакові повідомлення приходять одночасно на два різні потоки або різні сервери (наприклад, через агресивний ретрай балансувальника або паралельне перебалансування партицій у Kafka), простий шаблонний код виду `if (!exists()) { insert(); }` призведе до стану гонитви (*race condition*): обидва потоки одночасно перевірять наявність запису, обидва побачать, що запису ще немає, і обидва виконають бізнес-дію списання.

**Виправлення:**
Перевірка дубліката не повинна бути роздільною операцією читання та запису. Необхідно покладатися на атомарну вставку з обробкою конфлікту унікальності:

```sql
INSERT INTO inbox_messages (consumer_group, id, processed_at)
VALUES ('billing', 'tx_9981', NOW())
ON CONFLICT (consumer_group, id) DO NOTHING;
```

Якщо запис вставився (кількість змінених рядків `affected_rows == 1`), споживач продовжує виконання бізнес-мутації. Якщо рядок уже існував (`affected_rows == 0`), транзакція негайно пропускає бізнес-дію та переходить до відправки ACK брокеру.

### Пастка 3: Робота з Redis як проміжним кешем дедуплікації

У високонавантажених системах (понад 50 000 повідомлень/с) реляційна база даних не витримує перевірки кожного повідомлення. Тоді рівень L1 розширюють розподіленим сховищем Redis.

Для атомарної перевірки та взяття блокування в Redis застосовують команду `SET` з параметрами `NX` (встановити, лише якщо не існує) та `EX` (встановити час життя в секундах):

```
SET inbox:billing:tx_9981 "processing" NX EX 300
```

Якщо команда повернула `OK`, поточний робітник отримав ексклюзивне право на обробку повідомлення. Якщо команда повернула `nil`, повідомлення вже обробляється або було оброблене іншим робітником, і його слід відхилити.

**Важливий крайовий випадок (Fail-Open проти Fail-Closed):**
Що робити, якщо кластер Redis стає тимчасово недоступним через мережеве розділення?
- **Fail-Open (пріоритет доступності):** споживач ігнорує збій Redis і спускається на рівень L2 (реляційної бази даних). Навантаження на БД зростає, але дедуплікація не втрачається.
- **Fail-Closed (пріоритет захисту):** споживач відхиляє повідомлення та зупиняє споживання. Це захищає базу даних від лавиноподібного колапсу.

### Пастка 4: Неідемпотентні зовнішні побічні ефекти та Transactional Outbox

Якщо всередині транзакції споживача викликається сторонній REST API (наприклад, надсилання SMS-повідомлення або виклик платіжного шлюзу Stripe), відкат транзакції бази даних **не може відкликати вже відправлений мережевий запит**.

Якщо база впаде після виклику Stripe, клієнт отримає подвійне списання коштів на стороні платіжного провайдера.

**Правило архітектури:**
Усі зовнішні мережеві взаємодії виносяться за межі вхідної транзакції за допомогою патерна **Transactional Outbox**:

1. Вхідна транзакція лише записує стан у локальну базу даних та додає подію в таблицю `outbox_events`:
   ```sql
   INSERT INTO outbox_events (aggregate_id, event_type, payload)
   VALUES ('order_44', 'SEND_PAYMENT_REQUEST', '{"amount": 250.0}');
   ```
2. Окремий фоновий диспетчер (*outbox relay*) вичитує `outbox_events` і виконує мережевий виклик до Stripe, передаючи `idempotency_key = "order_44_stripe"`.
3. Навіть якщо диспетчер повторить виклик до Stripe десять разів, платіжний провайдер відсіче дублікати за власним ключем ідемпотентності.

### Пастка 5: Отруйні повідомлення (Poison Pills) та запис у DLQ

Якщо вхідне повідомлення містить пошкоджені бізнес-дані (наприклад, від'ємну суму транзакції або неіснуючий ідентифікатор рахунку), бізнес-логіка поверне помилку валідації. Якщо споживач просто відкотить транзакцію й не підтвердить повідомлення брокеру, брокер негайно відправить це повідомлення знову, блокуючи чергу назавжди.

**Виправлення:**
Споживач зобов'язаний зафіксувати неуспішний статус у таблиці `inbox_messages` і відправити повідомлення до мертвої черги (DLQ):

```sql
BEGIN;
INSERT INTO inbox_messages (id, consumer_group, status, error_details)
VALUES ('bad_msg_99', 'billing', 'REJECTED_VALIDATION', 'Некоректна сума: -500 грн')
ON CONFLICT (consumer_group, id) DO NOTHING;

INSERT INTO outbox_events (aggregate_id, event_type, payload)
VALUES ('bad_msg_99', 'SEND_TO_DLQ', '{"reason": "INVALID_AMOUNT"}');
COMMIT;
```

Транзакція успішно фіксує відхилення повідомлення, робітник відправляє `ACK` основній черзі, а пошкоджене повідомлення відправляється в DLQ для подальшого аналізу інженерами. Повторні доставки того самого отруйного повідомлення будуть миттєво відкинуті на кроці перевірки інбоксу без повторного виклику винятків.

## Тестування стійкості: хаос-ін'єкції та верифікація

Для перевірки коректності реалізації дедуплікації в автоматизованих тестах застосовують спеціальний тестовий стенд зі штучним внесенням відмов (*Chaos Testing Harness*):

1. **Ін'єкція випадкового падіння процесів (Crash Injection):** під час обробки 10 000 випадкових платежів тестовий фреймворк випадковим чином посилає сигнал `SIGKILL` споживачу на різних етапах (до транзакції, всередині транзакції, після транзакції перед ACK).
2. **Ін'єкція дублікатів (Duplicate Injection):** генератор навантаження навмисно дублює 30 % повідомлень із випадковими затримками від 10 мс до 5 секунд.
3. **Фінальна перевірка інваріанту (Invariant Assertion):** після завершення обробки всіх повідомлень тестовий стенд перевіряє фінальний баланс:
   ```
   підсумковий_баланс == початковий_баланс + сума_всіх_УНІКАЛЬНИХ_платежів
   ```
   Якщо хоча б один дублікат просочився або одне повідомлення загубилося, тест негайно падає з точним дампом журналу транзакцій.

## Метрики та спостережуваність (Observability)

Надійний споживач зобов'язаний експортувати метрики дедуплікації для систем моніторингу (Prometheus / Grafana).

Критичні показники для налаштування алертів:

```
# Лічильник оброблених повідомлень за статусами
messages_consumed_total{consumer_group="billing", status="processed"}
messages_consumed_total{consumer_group="billing", status="duplicate_l1_cache"}
messages_consumed_total{consumer_group="billing", status="duplicate_l2_db"}
messages_consumed_total{consumer_group="billing", status="error_tx"}

# Частка дублікатів у потоці
rate(messages_consumed_total{status=~"duplicate.*"}[5m]) / rate(messages_consumed_total[5m])
```

Якщо частка дублікатів перевищує 5 % у нормальному режимі роботи, це свідчить про системну проблему: занижений таймаут видимості в черзі (*visibility timeout*), занадто повільну обробку батчів або деградацію мережі між брокером та споживачами.
