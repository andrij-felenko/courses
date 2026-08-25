# ⚙️ Реалізація циклу повторних спроб із експоненційним відступом та джитером

В архітектурах із оптимістичним керуванням конкурентним доступом виявлення колізії (коли SQL-вираз повертає нуль змінених рядків `affected_rows == 0`) не є фатальною системною помилкою. Це штатний сигнал про те, що паралельний потік встиг зафіксувати свій стан раніше.

Якщо операція є програмною (наприклад, перерахунок лічильника переглядів, списання коштів із балансу за чергою повідомлень або оновлення залишків на складі), застосунок не повинен аварійно завершувати роботу. Замість цього він має виконати цикл повторної спроби (**Retry Loop**):
1. Повторно зчитати актуальний стан кортежу та його новий номер версії з бази даних.
2. Наново виконати бізнес-обчислення та перевірку інваріантів у пам'яті над свіжими даними.
3. Повторити спробу атомарної фіксації `UPDATE ... WHERE id = @id AND version = @new_v`.

Проте наївна реалізація повторних спроб, яка миттєво перезапускає транзакцію у разі колізії, створює небезпечну системну пастку — **лавину повторних спроб (Retry Storm)** та ефект «навали запитів» (**Thundering Herd**).

---

### Пастка синхронізованих повторів та порівняння стратегій відступу

Якщо кілька десятків конкурентних потоків одночасно намагаються оновити один і той самий «гарячий» запис, рівно один потік досягне успіху, а решта отримає колізію версії. Якщо всі потоки, що зазнали невдачі, одночасно зачекають фіксований проміжок часу (наприклад, 50 мілісекунд) і знову разом підуть до бази даних, вони гарантовано зіткнуться вдруге, втретє і вчетверте.

Така просторово-часова кореляція призводить до періодичних сплесків навантаження на базу даних, виснаження пулу з'єднань і різкого зростання затримок (Latency P99).

Для виходу з цього колапсу розроблено кілька математичних стратегій обчислення паузи `t_sleep`:

| Стратегія відступу | Формула обчислення затримки | Поведінка під час пікового навантаження |
|---|---|---|
| **Фіксований інтервал (Fixed Delay)** | `t = T_const` | Спричиняє періодичні синхронізовані хвилі навантаження; повна відсутність самозаспокоєння системи. |
| **Експоненційний без джитеру** | `t = min(T_max, T_base · 2^attempt)` | Збільшує інтервали між хвилями, але всі конфліктуючі потоки однієї хвилі все одно прокидаються одночасно. |
| **Половинний джитер (Equal Jitter)** | `half = min(T_max, T_base · 2^attempt) / 2; t = half + random(0, half)` | Гарантує мінімальну паузу, але зберігає часткову кореляцію фаз між потоками. |
| **Повний випадковий джитер (Full Jitter)** | `t = random(0, min(T_max, T_base · 2^attempt))` | Найкраще розмазує запити по часовій осі; забезпечує найкоротший сумарний час обслуговування черги. |
| **Декорельований джитер (Decorrelated Jitter)** | `t = min(T_max, random(T_base, t_prev · 3))` | Повністю усуває залежність від номера спроби; ідеальний для розподілених мережевих викликів. |

У більшості реляційних транзакційних систем стандартом є **Full Jitter**: він поєднує експоненційне зростання стелі очікування з рівномірним розподілом моменту старту кожної окремої спроби.

---

### Механіка реалізації на мовах C та C++

При проектуванні retry-контуру системного рівня необхідно враховувати три критичні аспекти взаємодії з операційною системою та компілятором:

1. **Безпека пауз до сигналів (POSIX Signal Interruption)**:
   Системний виклик `sleep()` або простий `usleep()` у POSIX-середовищах може бути достроково перерваний будь-яким сигналом ядра (наприклад, `SIGCHLD`, `SIGALRM` або сигналом профілювальника). Реалізація на C зобов'язана використовувати `nanosleep()` і в циклі перевіряти код помилки `errno == EINTR`, передаючи збережену структуру `rem` для досипання залишкового інтервалу. Без цього потоки прокидатимуться миттєво під час доставки сигналів, спричиняючи лавиноподібні повтори.

2. **Захист від бітового переповнення експоненти**:
   При обчисленні бітового зсуву `1ULL << attempt` значення `attempt` понад 63 призведе до невизначеної поведінки (Undefined Behavior). Застосування явного обмеження `std::min(attempt, 30u)` запобігає переповненню та стабілізує максимальну стелю затримки.

3. **Розподіл випадкових чисел та усунення зміщення залишку (Modulo Bias)**:
   Класичний вираз `rand() % N` у C має статистичну ваду — нерівномірний розподіл імовірностей для великих `N` (Modulo Bias). У C++ використовують генератор Вихору Мерсенна `std::mt19937` разом із `std::uniform_int_distribution`, що гарантує математично точний рівномірний розподіл інтервалів джитеру.

4. **Обробка результатів без винятків через `std::expected`**:
   У високонавантажених сервісах генерація C++ винятків (`throw OptimisticLockException`) на кожній колізії створює надмірне навантаження на таблиці розгортання стека (Stack Unwinding). Використання монадичного типу `std::expected<T, E>` із C++23 забезпечує нульові накладні витрати на передачу інформації про колізію через стек викликів.

---

### Повна реалізація механізму повторних спроб

Нижче наведено робочий приклад бібліотеки безпечного виконання оптимістичних транзакцій мовами C та C++.

Приклад моделює списання коштів із банківського рахунку: функція зчитує баланс і версію, перевіряє платоспроможність, намагається виконати CAS-оновлення, а в разі колізії версій виконує відступ із джитером до вичерпання ліміту спроб.

:::tabs
```c
#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <errno.h>

/* Структура банківського рахунку */
typedef struct {
    uint64_t account_id;
    int64_t balance_cents;
    uint64_t version;
} AccountRecord;

/* Коди результатів транзакції */
typedef enum {
    TX_SUCCESS = 0,
    TX_INSUFFICIENT_FUNDS = 1,
    TX_CONCURRENCY_CONFLICT = 2,
    TX_MAX_RETRIES_EXCEEDED = 3,
    TX_DB_ERROR = 4
} TxResult;

/* Конфігурація політики повторних спроб */
typedef struct {
    uint32_t max_retries;
    uint64_t base_delay_ms;
    uint64_t max_delay_ms;
} RetryPolicy;

/* Імітація сховища бази даних */
typedef struct {
    AccountRecord record;
    uint64_t update_attempts;
} MockDatabase;

/* Ініціалізація тестової бази даних */
void db_init(MockDatabase *db, uint64_t id, int64_t initial_balance) {
    db->record.account_id = id;
    db->record.balance_cents = initial_balance;
    db->record.version = 1;
    db->update_attempts = 0;
}

/* Читання запису: SELECT balance, version FROM accounts WHERE id = ? */
bool db_read_account(MockDatabase *db, uint64_t id, AccountRecord *out_record) {
    if (db->record.account_id != id) return false;
    *out_record = db->record;
    return true;
}

/* Атомарний CAS UPDATE:
   UPDATE accounts SET balance = ?, version = version + 1
   WHERE id = ? AND version = ? */
bool db_update_account_cas(MockDatabase *db, uint64_t id, int64_t new_balance, uint64_t expected_version) {
    db->update_attempts++;
    if (db->record.account_id != id) return false;
    
    // Перевірка предикату версії
    if (db->record.version != expected_version) {
        return false; // affected_rows = 0 (Колізія!)
    }

    // Атомарна фіксація
    db->record.balance_cents = new_balance;
    db->record.version++;
    return true; // affected_rows = 1 (Успіх)
}

/* Пауза з мікросекундною точністю та обробкою переривань EINTR */
static void sleep_ms(uint64_t ms) {
    struct timespec req, rem;
    req.tv_sec = (time_t)(ms / 1000);
    req.tv_nsec = (long)((ms % 1000) * 1000000L);
    while (nanosleep(&req, &rem) == -1 && errno == EINTR) {
        req = rem; // Досипаємо залишок часу, якщо потік був перерваний сигналом
    }
}

/* Обчислення паузи за алгоритмом Full Jitter */
static uint64_t calculate_backoff_ms(const RetryPolicy *policy, uint32_t attempt) {
    uint64_t multiplier = 1ULL << (attempt > 30 ? 30 : attempt);
    uint64_t max_backoff = policy->base_delay_ms * multiplier;
    if (max_backoff > policy->max_delay_ms) {
        max_backoff = policy->max_delay_ms;
    }
    if (max_backoff == 0) return 0;
    return (uint64_t)(rand() % (max_backoff + 1));
}

/* Виконання бізнес-операції з оптимістичним retry-циклом */
TxResult withdraw_with_retry(MockDatabase *db, uint64_t account_id, int64_t amount_cents, const RetryPolicy *policy) {
    for (uint32_t attempt = 0; attempt <= policy->max_retries; ++attempt) {
        AccountRecord acc;
        if (!db_read_account(db, account_id, &acc)) {
            return TX_DB_ERROR;
        }

        // Перевірка інваріантів бізнес-логіки
        if (acc.balance_cents < amount_cents) {
            return TX_INSUFFICIENT_FUNDS; // Повторювати немає сенсу
        }

        int64_t new_balance = acc.balance_cents - amount_cents;
        uint64_t current_version = acc.version;

        // Спроба атомарної фіксації
        bool success = db_update_account_cas(db, account_id, new_balance, current_version);
        if (success) {
            return TX_SUCCESS;
        }

        // Колізія: якщо спроби не вичерпано — відступаємо з джитером
        if (attempt < policy->max_retries) {
            uint64_t delay_ms = calculate_backoff_ms(policy, attempt);
            sleep_ms(delay_ms);
        }
    }

    return TX_MAX_RETRIES_EXCEEDED;
}

int main(void) {
    srand((unsigned int)time(NULL));
    MockDatabase db;
    db_init(&db, 42, 100000); // Баланс 100000 центів, версія 1

    RetryPolicy policy = {
        .max_retries = 5,
        .base_delay_ms = 10,
        .max_delay_ms = 200
    };

    printf("Початковий баланс: %ld центів, версія: %lu\n", db.record.balance_cents, db.record.version);
    
    TxResult res = withdraw_with_retry(&db, 42, 25000, &policy);
    if (res == TX_SUCCESS) {
        printf("Списання успішне! Новий баланс: %ld центів, нова версія: %lu\n",
               db.record.balance_cents, db.record.version);
    } else {
        printf("Помилка виконання транзакції: код %d\n", res);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <cstdint>
#include <random>
#include <chrono>
#include <thread>
#include <expected>
#include <functional>
#include <concepts>
#include <algorithm>

struct AccountRecord {
    uint64_t account_id{0};
    int64_t balance_cents{0};
    uint64_t version{0};
};

enum class TxError {
    NotFound,
    InsufficientFunds,
    ConcurrencyConflict,
    MaxRetriesExceeded,
    DatabaseError
};

struct RetryPolicy {
    uint32_t max_retries{5};
    std::chrono::milliseconds base_delay{10};
    std::chrono::milliseconds max_delay{200};
};

/* Інтерфейс репозиторію даних */
class MockAccountRepository {
public:
    explicit MockAccountRepository(uint64_t id, int64_t initial_balance)
        : record_{id, initial_balance, 1} {}

    [[nodiscard]] std::expected<AccountRecord, TxError> get_by_id(uint64_t id) const {
        if (record_.account_id != id) {
            return std::unexpected(TxError::NotFound);
        }
        return record_;
    }

    /* Атомарний CAS-запис */
    [[nodiscard]] std::expected<void, TxError> update_cas(uint64_t id, int64_t new_balance, uint64_t expected_version) {
        if (record_.account_id != id) {
            return std::unexpected(TxError::NotFound);
        }
        if (record_.version != expected_version) {
            return std::unexpected(TxError::ConcurrencyConflict); // affected_rows == 0
        }

        record_.balance_cents = new_balance;
        record_.version++;
        return {};
    }

private:
    AccountRecord record_;
};

/* Універсальний рандомізований генератор пауз (Full Jitter) */
class JitterBackoff {
public:
    explicit JitterBackoff(RetryPolicy policy)
        : policy_(policy), rng_(std::random_device{}()) {}

    void wait(uint32_t attempt) {
        uint64_t multiplier = 1ULL << std::min(attempt, 31u);
        auto calculated = policy_.base_delay * multiplier;
        auto capped = std::min(calculated, policy_.max_delay);

        std::uniform_int_distribution<uint64_t> dist(0, capped.count());
        auto actual_sleep = std::chrono::milliseconds(dist(rng_));
        
        std::this_thread::sleep_for(actual_sleep);
    }

private:
    RetryPolicy policy_;
    std::mt19937 rng_;
};

/* Узагальнений виконавець оптимістичних транзакцій */
template <typename TxFn>
auto execute_optimistic_retry(const RetryPolicy& policy, TxFn&& action)
    -> std::expected<typename std::invoke_result_t<TxFn>::value_type, TxError>
{
    JitterBackoff backoff(policy);

    for (uint32_t attempt = 0; attempt <= policy.max_retries; ++attempt) {
        auto result = action();
        if (result.has_value()) {
            return result.value();
        }

        // Якщо помилка не пов'язана з конкуренцією (наприклад, брак коштів) — не повторюємо
        if (result.error() != TxError::ConcurrencyConflict) {
            return std::unexpected(result.error());
        }

        if (attempt < policy.max_retries) {
            backoff.wait(attempt);
        }
    }

    return std::unexpected(TxError::MaxRetriesExceeded);
}

int main() {
    MockAccountRepository repo(42, 100000); // Баланс 100000 центів, версія 1
    RetryPolicy policy{.max_retries = 5, .base_delay = std::chrono::milliseconds(10), .max_delay = std::chrono::milliseconds(200)};

    uint64_t target_id = 42;
    int64_t withdraw_amount = 25000; // 25000 центів

    auto result = execute_optimistic_retry(policy, [&]() -> std::expected<AccountRecord, TxError> {
        // 1. Читання свіжого стану
        auto acc = repo.get_by_id(target_id);
        if (!acc) return std::unexpected(acc.error());

        // 2. Бізнес-перевірка
        if (acc->balance_cents < withdraw_amount) {
            return std::unexpected(TxError::InsufficientFunds);
        }

        // 3. Спроба фіксації
        int64_t new_balance = acc->balance_cents - withdraw_amount;
        auto update_res = repo.update_cas(target_id, new_balance, acc->version);
        if (!update_res) {
            return std::unexpected(update_res.error()); // ConcurrencyConflict
        }

        // Повертаємо оновлений об'єкт
        return AccountRecord{target_id, new_balance, acc->version + 1};
    });

    if (result.has_value()) {
        std::cout << "Транзакція успішна! Новий баланс: " << result->balance_cents 
                  << ", версія: " << result->version << '\n';
    } else {
        std::cerr << "Помилка транзакції, код: " << static_cast<int>(result.error()) << '\n';
    }

    return 0;
}
```
:::

---

### Тонкощі поведінки та граничні випадки у продакшені

1. **Неідемпотентні побічні ефекти**:
   Бізнес-логіка всередині retry-блоку **не повинна** виконувати зовнішніх невідворотних дій (наприклад, надсилати HTTP-запити до платіжного шлюзу Stripe чи відправляти e-mail користувачеві) до успішної фіксації транзакції. Усі побічні ефекти мають генеруватися у вигляді подій у транзакційному буфері (патерн Transactional Outbox) і публікуватися назовні лише після того, як `execute_optimistic_retry` поверне успіх.

2. **Захист від виснаження пулу з'єднань**:
   Під час затримки `std::this_thread::sleep_for` або `sleep_ms` з'єднання з базою даних не повинно утримувати відкриту транзакцію СУБД. Потік має виконувати окремі короткі запити `SELECT` та `UPDATE` у режимі автофіксації (`autocommit`) або відкривати й закривати транзакцію на кожній спробі окремо. Утримання відкритої транзакції під час очікування таймера паралізує пул з'єднань застосунку і призводить до вичерпання дескрипторів сокетів.

3. **Обмеження сумарного часу виконання (Deadline / Context Timeout)**:
   Окрім лічильника `max_retries`, промислові реалізації завжди перевіряють абсолютний дедлайн операції (`context.WithTimeout` або `std::chrono::steady_clock`). Якщо загальний час повторів перевищує встановлений SLA (наприклад, 2 секунди), операція негайно переривається незалежно від кількості невикористаних спроб.

4. **Телеметрія та моніторинг колізій**:
   Для виявлення вузьких місць у продакшені retry-контур обов'язково повинен експортувати метрики до систем спостережуваності (Prometheus/OpenTelemetry):
   - Лічильник загальної кількості колізій: `occ_conflicts_total{table="accounts"}`.
   - Розподіл кількості спроб (Histogram): `occ_retry_attempts_bucket{le="1"}, {le="2"}, {le="5"}`.
   - Якщо частка операцій, які потребують більше однієї спроби, стабільно перевищує 5%, це свідчить про появу надмірно гарячого ключа (Hotspot), що вимагає зміни моделі даних або переходу на шардування лічильників.
