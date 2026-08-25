# ⚙️ Практичне відтворення аномалій та безпечний цикл повторів у C++ і C

Розробка надійних систем обробки транзакцій вимагає не лише теоретичного розуміння рівнів ізоляції, але й уміння практично відтворювати конкурентні дефекти та захищати прикладний код від раптових відкатів. Будь-який рушій, що працює на строгих рівнях ізоляції (таких як `REPEATABLE READ` або `SERIALIZABLE` в PostgreSQL), гарантує цілісність даних ціною примусового переривання транзакцій при виявленні конфліктів (помилка `SQLSTATE 40001: serialization_failure`).

У цій вставці реалізовано повноцінний випробувальний стенд: модель виникнення аномалії втраченого оновлення (Lost Update), аномалії зсуву запису (Write Skew) та індустріальний механізм автоматичного повторення транзакцій з експоненційним відкладанням і рандомізованим джитером (*Exponential Backoff with Full Jitter*).

## Архітектура стенду та механіка конкурентних гонок

Стенд моделює роботу клієнтської програми з базою даних через шар абстракції транзакційного контексту:

### 1. Механіка відтворення Lost Update (Втрачене оновлення)
Аномалія втраченого оновлення виникає в класичному патерні «прочитав — модифікував — записав» (*Read-Modify-Write*).
Нехай початковий баланс рахунку в сховищі становить 1000 грн. Два паралельні потоки (клієнти A та B) одночасно намагаються поповнити рахунок на 100 грн кожен:
- Потік A зчитує `balance = 1000`.
- Потік B зчитує `balance = 1000` (до того, як A записав результат).
- Потік A обчислює `1000 + 100 = 1100` і записує `balance = 1100`.
- Потік B обчислює `1000 + 100 = 1100` і записує `balance = 1100`, повністю затираючи внесок потоку A.

На рівні `Read Committed` СУБД дозволяє обом транзакціям успішно зафіксуватися, оскільки кожна операція запису виконується над останнім зафіксованим рядком, але логічне значення оновлення було обчислене на застарілих даних. На рівнях `Repeatable Read` або `Serializable` рушій відстежує паралельну модифікацію того самого рядка і перериває транзакцію, яка спробувала записати зміни другою.

### 2. Механіка відтворення Write Skew (Зсув запису)
У сценарії чергування лікарів діє глобальне бізнес-правило: у відділенні завжди має чергувати хоча б один лікар (`count(on_call) >= 1`).
- У системі чергують Аліса та Боб (`count = 2`).
- Лікар Аліса у своїй транзакції зчитує загальну кількість чергових: запит повертає 2. Оскільки умова `2 >= 2` виконується, транзакція Аліси готує оновлення `Alice.on_call = false`.
- Одночасно лікар Боб у своїй транзакції зчитує той самий знімок: запит повертає 2. Боб також отримує дозвіл і готує оновлення `Bob.on_call = false`.
- Обидві транзакції виконують `COMMIT`. Під Snapshot Isolation обидва коміти успішні, оскільки Аліса змінювала рядок зі своїм ID, а Боб — зі своїм ID (неперетинні множини запису).
- Кінцевий стан: жодного лікаря немає на чергуванні (`count = 0`).

Для запобігання цій аномалії в чистому MVCC необхідний механізм відстеження антизалежностей читання-запису (SSI) або явне блокування всього діапазону чергових через `SELECT ... FOR UPDATE`.

### 3. Математика експоненційного відкладання з джитером (Full Jitter)
Якщо дві транзакції стикаються з конфліктом серіалізації й СУБД відкочує одну з них, простий негайний перезапуск призведе до повторного зіткнення з високою ймовірністю. Фіксована затримка (наприклад, 50 мс) також неефективна: якщо десяток паралельних воркерів зіткнулися водночас, вони прокидатимуться синхронними хвилями, створюючи періодичні пікові навантаження (*Thundering Herd Problem*).

Алгоритм **Full Jitter** (розроблений інженерами Amazon Web Services) обчислює інтервал сну `T_sleep` за формулою:

```
T_backoff = min(T_max, T_base · 2^(attempt - 1))
T_sleep   = UniformRandom(0, T_backoff)
```

Рівномірний випадковий розподіл від 0 до експоненційної стелі гарантує, що черга конфліктних запитів миттєво розсіюється по часовій осі, а пропускна здатність системи під високим навантаженням досягає теоретичного максимуму.

## Реалізація стенду мовами C++ та C

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <thread>
#include <mutex>
#include <atomic>
#include <random>
#include <chrono>
#include <expected>
#include <functional>

// Стан коду помилки транзакційного рушія
enum class TxStatus {
    Success,
    SerializationFailure, // SQLSTATE 40001
    DeadlockDetected,     // SQLSTATE 40P01
    ConstraintViolation,  // Порушення бізнес-інваріанта
    FatalError
};

// Проста імітація сховища бази даних (In-Memory Database Storage)
struct DatabaseState {
    std::mutex mtx;
    int account_balance{1000};
    bool doctor_alice_on_call{true};
    bool doctor_bob_on_call{true};
    uint64_t current_version{1};
};

// Контекст транзакції з RAII-керуванням життєвим циклом
class TransactionContext {
public:
    explicit TransactionContext(DatabaseState& db, uint64_t tx_id)
        : db_(db), tx_id_(tx_id), snapshot_version_(db.current_version) {}

    // Імітація читання балансу (Snapshot Read)
    int read_balance() const {
        return db_.account_balance;
    }

    // Імітація конкурентного запису балансу
    TxStatus update_balance(int new_balance, bool simulate_conflict = false) {
        if (simulate_conflict) {
            return TxStatus::SerializationFailure;
        }
        db_.account_balance = new_balance;
        return TxStatus::Success;
    }

    // Перевірка інваріанта чергування лікарів
    int count_active_doctors() const {
        int active = 0;
        if (db_.doctor_alice_on_call) ++active;
        if (db_.doctor_bob_on_call) ++active;
        return active;
    }

    TxStatus resign_doctor(std::string_view doctor_name) {
        if (doctor_name == "Alice") {
            db_.doctor_alice_on_call = false;
        } else if (doctor_name == "Bob") {
            db_.doctor_bob_on_call = false;
        }
        return TxStatus::Success;
    }

    uint64_t id() const noexcept { return tx_id_; }
    uint64_t snapshot_version() const noexcept { return snapshot_version_; }

private:
    DatabaseState& db_;
    uint64_t tx_id_{0};
    uint64_t snapshot_version_{0};
};

// Індустріальний виконавець транзакцій з алгоритмом Exponential Backoff + Jitter
class TransactionRunner {
public:
    struct RetryPolicy {
        int max_retries{5};
        std::chrono::milliseconds initial_backoff{20};
        std::chrono::milliseconds max_backoff{500};
    };

    explicit TransactionRunner(DatabaseState& db, RetryPolicy policy = {})
        : db_(db), policy_(policy) {}

    template <typename Func>
    std::expected<void, TxStatus> run(Func&& operation) {
        std::random_device rd;
        std::mt19937 gen(rd());

        auto current_backoff = policy_.initial_backoff;

        for (int attempt = 1; attempt <= policy_.max_retries; ++attempt) {
            uint64_t tx_id = next_tx_id_.fetch_add(1, std::memory_order_relaxed);
            TransactionContext ctx(db_, tx_id);

            TxStatus status = operation(ctx);

            if (status == TxStatus::Success) {
                return {};
            }

            // Повторюємо лише при помилках серіалізації та взаємних блокуваннях
            if (status == TxStatus::SerializationFailure || status == TxStatus::DeadlockDetected) {
                if (attempt == policy_.max_retries) {
                    return std::unexpected(status);
                }

                // Обчислення випадкового джитеру (Full Jitter: random between 0 and current_backoff)
                std::uniform_int_distribution<int64_t> dist(0, current_backoff.count());
                auto sleep_duration = std::chrono::milliseconds(dist(gen));

                std::this_thread::sleep_for(sleep_duration);

                // Експоненційне зростання затримки з обмеженням стелі
                current_backoff = std::min(current_backoff * 2, policy_.max_backoff);
                continue;
            }

            // Усі інші помилки вважаються фатальними й негайно повертаються
            return std::unexpected(status);
        }

        return std::unexpected(TxStatus::SerializationFailure);
    }

private:
    DatabaseState& db_;
    RetryPolicy policy_;
    inline static std::atomic<uint64_t> next_tx_id_{1};
};

// Демонстрація роботи стенду
int main() {
    DatabaseState db;
    TransactionRunner runner(db);

    std::cout << "[INFO] Початковий баланс рахунку: " << db.account_balance << " грн\n";

    // Спроба безпечного паралельного переказу коштів
    auto tx_action = [](TransactionContext& ctx) -> TxStatus {
        int current = ctx.read_balance();
        // Імітація рідкісного конфлікту при першій спробі
        static std::atomic<int> attempt_counter{0};
        bool conflict = (attempt_counter.fetch_add(1) % 2 == 1);

        std::cout << "  -> Транзакція #" << ctx.id() << ": зчитано баланс = " << current << "\n";
        return ctx.update_balance(current + 100, conflict);
    };

    auto res = runner.run(tx_action);
    if (res.has_value()) {
        std::cout << "[SUCCESS] Транзакція успішно зафіксована. Новий баланс: " 
                  << db.account_balance << " грн\n";
    } else {
        std::cout << "[ERROR] Транзакція відхилена після вичерпання спроб.\n";
    }

    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
static void sleep_ms(int ms) { Sleep(ms); }
#else
#include <unistd.h>
static void sleep_ms(int ms) { usleep(ms * 1000); }
#endif

typedef enum {
    TX_SUCCESS = 0,
    TX_SERIALIZATION_FAILURE = 1, // SQLSTATE 40001
    TX_DEADLOCK_DETECTED = 2,     // SQLSTATE 40P01
    TX_FATAL_ERROR = 3
} TxStatus;

typedef struct {
    int account_balance;
    bool doctor_alice_on_call;
    bool doctor_bob_on_call;
    uint64_t current_version;
} DatabaseState;

typedef struct {
    DatabaseState* db;
    uint64_t tx_id;
    uint64_t snapshot_version;
} TransactionContext;

typedef struct {
    int max_retries;
    int initial_backoff_ms;
    int max_backoff_ms;
} RetryPolicy;

static uint64_t g_next_tx_id = 1;

void tx_init_context(TransactionContext* ctx, DatabaseState* db) {
    ctx->db = db;
    ctx->tx_id = g_next_tx_id++;
    ctx->snapshot_version = db->current_version;
}

int tx_read_balance(const TransactionContext* ctx) {
    return ctx->db->account_balance;
}

TxStatus tx_update_balance(TransactionContext* ctx, int new_balance, bool simulate_conflict) {
    if (simulate_conflict) {
        return TX_SERIALIZATION_FAILURE;
    }
    ctx->db->account_balance = new_balance;
    return TX_SUCCESS;
}

typedef TxStatus (*TxOperationFunc)(TransactionContext* ctx, void* user_data);

TxStatus tx_runner_execute(DatabaseState* db, const RetryPolicy* policy, 
                          TxOperationFunc operation, void* user_data) {
    int current_backoff = policy->initial_backoff_ms;

    for (int attempt = 1; attempt <= policy->max_retries; ++attempt) {
        TransactionContext ctx;
        tx_init_context(&ctx, db);

        TxStatus status = operation(&ctx, user_data);

        if (status == TX_SUCCESS) {
            return TX_SUCCESS;
        }

        if (status == TX_SERIALIZATION_FAILURE || status == TX_DEADLOCK_DETECTED) {
            if (attempt == policy->max_retries) {
                return status;
            }

            // Обчислення рандомізованого джитеру
            int sleep_time = rand() % (current_backoff + 1);
            sleep_ms(sleep_time);

            // Подвоєння затримки
            current_backoff *= 2;
            if (current_backoff > policy->max_backoff_ms) {
                current_backoff = policy->max_backoff_ms;
            }
            continue;
        }

        return status;
    }

    return TX_SERIALIZATION_FAILURE;
}

static int g_attempt_counter = 0;

TxStatus sample_operation(TransactionContext* ctx, void* user_data) {
    (void)user_data;
    int current = tx_read_balance(ctx);
    bool conflict = (++g_attempt_counter % 2 == 1);

    printf("  -> [C] Транзакція #%llu: зчитано баланс = %d (конфлікт: %s)\n",
           (unsigned long long)ctx->tx_id, current, conflict ? "ТАК" : "НІ");

    return tx_update_balance(ctx, current + 100, conflict);
}

int main(void) {
    srand((unsigned int)time(NULL));

    DatabaseState db;
    db.account_balance = 1000;
    db.doctor_alice_on_call = true;
    db.doctor_bob_on_call = true;
    db.current_version = 1;

    RetryPolicy policy = {
        .max_retries = 5,
        .initial_backoff_ms = 20,
        .max_backoff_ms = 500
    };

    printf("[INFO C] Початковий баланс: %d грн\n", db.account_balance);

    TxStatus status = tx_runner_execute(&db, &policy, sample_operation, NULL);

    if (status == TX_SUCCESS) {
        printf("[SUCCESS C] Фіксація успішна! Залишок: %d грн\n", db.account_balance);
    } else {
        printf("[ERROR C] Транзакцію відхилено після вичерпання спроб (код %d)\n", status);
    }

    return 0;
}
```
:::

## Інженерні правила та тонкощі обробки помилок серіалізації

При написанні клієнтського коду, що взаємодіє з базою даних на високих рівнях ізоляції, слід неухильно дотримуватися п'яти фундаментальних інженерних правил:

1. **Ідемпотентність тіла транзакції**:
   Оскільки транзакція може перезапускатися кілька разів, усередині її тіла категорично заборонено виконувати невідкличні зовнішні побічні ефекти (відправка HTTP-запитів, списування коштів через банківський API, генерація push-повідомлень чи публікація повідомлень у чергу Kafka). Якщо транзакція відкотиться після виконання HTTP-запиту, зовнішній платіж уже не повернеться. Усі зовнішні взаємодії повинні відкладатися до моменту, коли транзакція гарантовано успішно виконає `COMMIT` (патерн *Transactional Outbox*).

2. **Обов'язковий випадковий джитер (Full Jitter)**:
   Якщо дві паралельні транзакції зіткнулися з конфліктом серіалізації й одночасно перезапустяться через фіксований інтервал часу (наприклад, рівно через 50 мс), вони гарантовано зіткнуться знову в тій самій точці коду. Рандомізація затримки за законом рівномірного розподілу розсіює чергу запитів у часі й повністю усуває самосинхронізацію та взаємні блокування.

3. **Обмеження кількості повторів (Retry Limit) та дедлайни**:
   Нескінченний цикл повторів може намертво заблокувати потік обробки під час системних сплесків навантаження. Рекомендований ліміт спроб становить від 3 до 5 ітерацій, після чого помилка має прокидатися на рівень користувача із зрозумілим повідомленням або перенаправлятися у чергу відкладених завдань (*Dead Letter Queue*).

4. **Очищення стану підключення в пулі з'єднань**:
   Якщо транзакція зазнала невдачі на середині виконання, з'єднання залишається в аварійному стані (`SQLSTATE 25P02: current transaction is aborted, commands ignored until end of transaction block`). Виконавець транзакцій обов'язково повинен виконати явний `ROLLBACK` перед поверненням сокета в пул з'єднань, інакше наступний запит іншого користувача зазнає миттєвого збою.

5. **Часткові повтори через точки збереження (Savepoints)**:
   Якщо транзакція виконує великий обсяг роботи, а конфлікт виникає лише на фінальній стадії оновлення лічильника, перезапускати всю транзакцію від самого початку занадто дорого. У таких випадках навколо конфліктного блоку створюється точка збереження (`SAVEPOINT sp1; ... ROLLBACK TO SAVEPOINT sp1;`), що дозволяє перезапустити лише останню дію без скидання раніше зчитаних та обчислених даних.
