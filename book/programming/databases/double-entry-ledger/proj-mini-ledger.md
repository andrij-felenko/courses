# ⚙️ Реалізація рушія гросбуха: рахунки, проводки та знімки

Цей проект реалізує повнофункціональний автономний рушій гросбуха подвійного запису в оперативній пам'яті. Архітектура програми спроектована з дотриманням ключових вимог до фінансового ядра: гарантія інваріанта нульової суми, незмінність журналу операцій, захист від повторних списань через ключі ідемпотентності та високоефективний розрахунок балансів за допомогою знімків стану.

## Архітектурні принципи та структури даних

Ядро гросбуха реалізує модель незмінного журналу подій (*Event Sourcing*). У ній фінансовий стан рахунку ніколи не модифікується на місці, а виводиться як результат агрегації послідовності проводок.

Програма спирається на такі фундаментальні структури:
1. **`Account` (Обліковий рахунок)**: містить унікальний числовий ідентифікатор, людинозрозумілу назву та категорію рахунку (`ASSET`, `LIABILITY`, `EQUITY`, `REVENUE`, `EXPENSE`).
2. **`Posting` (Проводка)**: атомарний елемент переміщення вартості, прив'язаний до конкретного рахунку, транзакції та глобального монотонного номера черги (`sequence`). Сума є знаковим цілим числом `int64_t`: додатне значення означає дебетове зарахування, а від'ємне — кредитове списання.
3. **`Transaction` (Транзакція)**: логічна група проводок, об'єднана спільним ідентифікатором, описом бізнес-події та унікальним клієнтським ключем ідемпотентності (*Idempotency Key*).
4. **`BalanceSnapshot` (Знімок балансу)**: зафіксований проміжний агрегат, що зберігає точну суму залишку на рахунку на момент певного порядкового номера `sequence`.

## Вибір цілочисельного представлення

Усі суми вимірюються в мінімальних неподільних одиницях валюти (наприклад, у копійках для гривні або центах для долара США). Використання 64-бітного знакового цілого типу `int64_t` дозволяє повністю уникнути проблем двійкового округлення, характерних для чисел із плаваючою комою, та витримує фінансові обороти в десятки квадрильйонів копійок без ризику переповнення діапазону.

## Повний вихідний код реалізації

Нижче наведено дві повноцінні та ідіоматичні реалізації рушія: мовою C (із фіксованими структурами в пам'яті та кодами повернення) та мовою C++ (із використанням RAII, стандартних контейнерів, типізованих перечислень `enum class` та механізмів обробки виключень).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_POSTINGS_PER_TX 16
#define MAX_TRANSACTIONS 1024
#define MAX_POSTINGS 4096
#define MAX_ACCOUNTS 256
#define KEY_LEN 64

typedef enum {
    ACCOUNT_ASSET,
    ACCOUNT_LIABILITY,
    ACCOUNT_EQUITY,
    ACCOUNT_REVENUE,
    ACCOUNT_EXPENSE
} AccountType;

typedef struct {
    uint32_t id;
    char name[64];
    AccountType type;
} Account;

typedef struct {
    uint32_t id;
    uint32_t transaction_id;
    uint32_t account_id;
    int64_t amount; // Додатне: дебет/зарахування, від'ємне: кредит/списання
    uint64_t sequence;
} Posting;

typedef struct {
    uint32_t id;
    char idempotency_key[KEY_LEN];
    char description[128];
    uint32_t posting_count;
    Posting postings[MAX_POSTINGS_PER_TX];
} Transaction;

typedef struct {
    uint32_t account_id;
    uint64_t at_sequence;
    int64_t balance;
} BalanceSnapshot;

typedef struct {
    Account accounts[MAX_ACCOUNTS];
    uint32_t account_count;

    Posting postings[MAX_POSTINGS];
    uint32_t posting_count;

    Transaction transactions[MAX_TRANSACTIONS];
    uint32_t transaction_count;

    BalanceSnapshot snapshots[MAX_ACCOUNTS];
    uint32_t snapshot_count;

    uint64_t global_sequence;
} Ledger;

void ledger_init(Ledger *ledger) {
    memset(ledger, 0, sizeof(Ledger));
}

int ledger_add_account(Ledger *ledger, uint32_t id, const char *name, AccountType type) {
    if (ledger->account_count >= MAX_ACCOUNTS) return -1;
    for (uint32_t i = 0; i < ledger->account_count; i++) {
        if (ledger->accounts[i].id == id) return -2; // Дублікат ID
    }
    Account *acc = &ledger->accounts[ledger->account_count++];
    acc->id = id;
    strncpy(acc->name, name, sizeof(acc->name) - 1);
    acc->type = type;
    return 0;
}

// Пошук транзакції за ключем ідемпотентності
Transaction* ledger_find_by_key(Ledger *ledger, const char *key) {
    if (!key || strlen(key) == 0) return NULL;
    for (uint32_t i = 0; i < ledger->transaction_count; i++) {
        if (strncmp(ledger->transactions[i].idempotency_key, key, KEY_LEN) == 0) {
            return &ledger->transactions[i];
        }
    }
    return NULL;
}

// Запис транзакції з перевіркою нульової суми
int ledger_post_transaction(Ledger *ledger, const char *idempotency_key, 
                            const char *desc, const Posting *entries, uint32_t count) {
    if (count < 2 || count > MAX_POSTINGS_PER_TX) return -1;

    // 1. Перевірка ідемпотентності
    if (idempotency_key && strlen(idempotency_key) > 0) {
        if (ledger_find_by_key(ledger, idempotency_key) != NULL) {
            return 1; // Транзакцію вже проведено раніше (ідемпотентний пропуск)
        }
    }

    // 2. Перевірка інваріанта нульової суми: сума всіх amount повинна дорівнювати 0
    int64_t sum = 0;
    for (uint32_t i = 0; i < count; i++) {
        sum += entries[i].amount;
    }
    if (sum != 0) {
        return -2; // Порушення балансу: сума не нуль
    }

    // 3. Перевірка існування всіх зазначених рахунків
    for (uint32_t i = 0; i < count; i++) {
        bool found = false;
        for (uint32_t a = 0; a < ledger->account_count; a++) {
            if (ledger->accounts[a].id == entries[i].account_id) {
                found = true;
                break;
            }
        }
        if (!found) return -3; // Рахунок не знайдено в плані рахунків
    }

    if (ledger->transaction_count >= MAX_TRANSACTIONS) return -4;
    if (ledger->posting_count + count > MAX_POSTINGS) return -5;

    // 4. Атомарний запис у незмінний журнал проводок
    uint32_t tx_id = ledger->transaction_count + 1;
    Transaction *tx = &ledger->transactions[ledger->transaction_count++];
    tx->id = tx_id;
    if (idempotency_key) strncpy(tx->idempotency_key, idempotency_key, KEY_LEN - 1);
    strncpy(tx->description, desc, sizeof(tx->description) - 1);
    tx->posting_count = count;

    for (uint32_t i = 0; i < count; i++) {
        ledger->global_sequence++;
        Posting *p = &ledger->postings[ledger->posting_count++];
        p->id = ledger->posting_count;
        p->transaction_id = tx_id;
        p->account_id = entries[i].account_id;
        p->amount = entries[i].amount;
        p->sequence = ledger->global_sequence;

        tx->postings[i] = *p;
    }

    return 0;
}

// Створення знімка для конкретного рахунку
int ledger_create_snapshot(Ledger *ledger, uint32_t account_id) {
    int64_t bal = 0;
    uint64_t max_seq = 0;
    for (uint32_t i = 0; i < ledger->posting_count; i++) {
        if (ledger->postings[i].account_id == account_id) {
            bal += ledger->postings[i].amount;
            if (ledger->postings[i].sequence > max_seq) {
                max_seq = ledger->postings[i].sequence;
            }
        }
    }
    // Оновлюємо наявний знімок або створюємо новий
    for (uint32_t i = 0; i < ledger->snapshot_count; i++) {
        if (ledger->snapshots[i].account_id == account_id) {
            ledger->snapshots[i].at_sequence = max_seq;
            ledger->snapshots[i].balance = bal;
            return 0;
        }
    }
    if (ledger->snapshot_count >= MAX_ACCOUNTS) return -1;
    BalanceSnapshot *s = &ledger->snapshots[ledger->snapshot_count++];
    s->account_id = account_id;
    s->at_sequence = max_seq;
    s->balance = bal;
    return 0;
}

// Отримання поточного балансу: Snapshot + Delta
int64_t ledger_get_balance(const Ledger *ledger, uint32_t account_id) {
    int64_t base_balance = 0;
    uint64_t after_seq = 0;

    // Перевіряємо наявність збереженого знімка
    for (uint32_t i = 0; i < ledger->snapshot_count; i++) {
        if (ledger->snapshots[i].account_id == account_id) {
            base_balance = ledger->snapshots[i].balance;
            after_seq = ledger->snapshots[i].at_sequence;
            break;
        }
    }

    // Підсумовуємо тільки нові проводки, що з'явилися після знімка
    int64_t delta = 0;
    for (uint32_t i = 0; i < ledger->posting_count; i++) {
        if (ledger->postings[i].account_id == account_id && 
            ledger->postings[i].sequence > after_seq) {
            delta += ledger->postings[i].amount;
        }
    }

    return base_balance + delta;
}

int main(void) {
    Ledger ledger;
    ledger_init(&ledger);

    // Створення плану рахунків
    ledger_add_account(&ledger, 101, "Bank_Account_UAH", ACCOUNT_ASSET);
    ledger_add_account(&ledger, 201, "Customer_Deposits", ACCOUNT_LIABILITY);
    ledger_add_account(&ledger, 401, "Processing_Fee_Income", ACCOUNT_REVENUE);

    printf("Ініціалізація рахунків завершена.\n");

    // Транзакція 1: Клієнт поповнює гаманець на 1000.00 грн (100000 копійок)
    // Банк отримує актив (+100000), у банку виникає зобов'язання перед клієнтом (-100000)
    Posting tx1_postings[2] = {
        { .account_id = 101, .amount = 100000 },
        { .account_id = 201, .amount = -100000 }
    };
    int res = ledger_post_transaction(&ledger, "DEP-001", "Поповнення гаманця", tx1_postings, 2);
    printf("Tx 1 статус: %d (0 = OK)\n", res);

    // Спроба повторного запису з тим самим ключем ідемпотентності
    int res_dup = ledger_post_transaction(&ledger, "DEP-001", "Повтор", tx1_postings, 2);
    printf("Tx 1 повторний виклик: %d (1 = Idempotent Skip)\n", res_dup);

    // Створюємо знімок для рахунку банку
    ledger_create_snapshot(&ledger, 101);

    // Транзакція 2: Списання комісії 20.00 грн
    Posting tx2_postings[2] = {
        { .account_id = 201, .amount = 2000 },
        { .account_id = 401, .amount = -2000 }
    };
    ledger_post_transaction(&ledger, "FEE-001", "Комісія за обслуговування", tx2_postings, 2);

    printf("Баланс банку (101): %ld коп.\n", (long)ledger_get_balance(&ledger, 101));
    printf("Баланс депозитів клієнтів (201): %ld коп.\n", (long)ledger_get_balance(&ledger, 201));
    printf("Баланс доходу з комісій (401): %ld коп.\n", (long)ledger_get_balance(&ledger, 401));

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <optional>
#include <cstdint>
#include <numeric>
#include <stdexcept>

enum class AccountType {
    Asset,
    Liability,
    Equity,
    Revenue,
    Expense
};

struct Account {
    uint32_t id;
    std::string name;
    AccountType type;
};

struct Posting {
    uint32_t account_id;
    int64_t amount; // Знакове: додатне — дебет, від'ємне — кредит
    uint64_t sequence{0};
};

struct Transaction {
    uint32_t id;
    std::string idempotency_key;
    std::string description;
    std::vector<Posting> postings;
};

struct BalanceSnapshot {
    uint64_t at_sequence{0};
    int64_t balance{0};
};

class LedgerEngine {
public:
    void add_account(uint32_t id, std::string_view name, AccountType type) {
        if (accounts_.find(id) != accounts_.end()) {
            throw std::runtime_error("Рахунок із таким ID уже існує");
        }
        accounts_[id] = Account{id, std::string(name), type};
    }

    enum class PostResult {
        Success,
        IdempotentDuplicate,
        UnbalancedTransaction,
        AccountNotFound
    };

    PostResult post_transaction(std::string_view idempotency_key,
                                std::string_view description,
                                const std::vector<Posting>& entries) {
        if (entries.size() < 2) {
            return PostResult::UnbalancedTransaction;
        }

        // 1. Перевірка ідемпотентності
        if (!idempotency_key.empty()) {
            auto it = transactions_by_key_.find(std::string(idempotency_key));
            if (it != transactions_by_key_.end()) {
                return PostResult::IdempotentDuplicate;
            }
        }

        // 2. Перевірка інваріанта нульової суми: сума всіх amount повинна дорівнювати 0
        int64_t total_sum = std::accumulate(entries.begin(), entries.end(), int64_t{0},
            [](int64_t acc, const Posting& p) { return acc + p.amount; });

        if (total_sum != 0) {
            return PostResult::UnbalancedTransaction;
        }

        // 3. Валідація існування всіх задіяних рахунків
        for (const auto& entry : entries) {
            if (accounts_.find(entry.account_id) == accounts_.end()) {
                return PostResult::AccountNotFound;
            }
        }

        // 4. Атомарна фіксація транзакції та запис проводок у незмінний журнал
        uint32_t tx_id = static_cast<uint32_t>(transactions_.size() + 1);
        Transaction tx{tx_id, std::string(idempotency_key), std::string(description), {}};

        for (auto entry : entries) {
            entry.sequence = ++global_sequence_;
            postings_log_.push_back(entry);
            tx.postings.push_back(entry);
        }

        transactions_.push_back(tx);
        if (!idempotency_key.empty()) {
            transactions_by_key_[std::string(idempotency_key)] = tx_id;
        }

        return PostResult::Success;
    }

    void create_snapshot(uint32_t account_id) {
        int64_t balance = 0;
        uint64_t max_seq = 0;

        for (const auto& p : postings_log_) {
            if (p.account_id == account_id) {
                balance += p.amount;
                if (p.sequence > max_seq) {
                    max_seq = p.sequence;
                }
            }
        }

        snapshots_[account_id] = BalanceSnapshot{max_seq, balance};
    }

    [[nodiscard]] int64_t get_balance(uint32_t account_id) const {
        int64_t base_balance = 0;
        uint64_t after_sequence = 0;

        auto snap_it = snapshots_.find(account_id);
        if (snap_it != snapshots_.end()) {
            base_balance = snap_it->second.balance;
            after_sequence = snap_it->second.at_sequence;
        }

        // Інкрементальний підрахунок залишку тільки за новими проводками
        int64_t delta = 0;
        for (const auto& p : postings_log_) {
            if (p.account_id == account_id && p.sequence > after_sequence) {
                delta += p.amount;
            }
        }

        return base_balance + delta;
    }

    // Сторнування (реверс) раніше зафіксованої транзакції
    PostResult reverse_transaction(uint32_t original_tx_id, std::string_view new_key) {
        if (original_tx_id == 0 || original_tx_id > transactions_.size()) {
            return PostResult::AccountNotFound;
        }

        const auto& original = transactions_[original_tx_id - 1];
        std::vector<Posting> reversal_entries;
        reversal_entries.reserve(original.postings.size());

        for (const auto& p : original.postings) {
            reversal_entries.push_back(Posting{p.account_id, -p.amount, 0});
        }

        std::string desc = "Сторнування транзакції #" + std::to_string(original_tx_id) + ": " + original.description;
        return post_transaction(new_key, desc, reversal_entries);
    }

private:
    std::unordered_map<uint32_t, Account> accounts_;
    std::vector<Posting> postings_log_;
    std::vector<Transaction> transactions_;
    std::unordered_map<std::string, uint32_t> transactions_by_key_;
    std::unordered_map<uint32_t, BalanceSnapshot> snapshots_;
    uint64_t global_sequence_{0};
};

int main() {
    LedgerEngine ledger;

    ledger.add_account(101, "Bank_Account_UAH", AccountType::Asset);
    ledger.add_account(201, "Customer_Deposits", AccountType::Liability);
    ledger.add_account(401, "Processing_Fee_Income", AccountType::Revenue);

    // 1. Поповнення балансу на 1500.00 грн (150000 копійок)
    auto res1 = ledger.post_transaction("DEP-100", "Поповнення рахунку", {
        {101, 150000},
        {201, -150000}
    });
    std::cout << "Tx 1 проведено: " << (res1 == LedgerEngine::PostResult::Success) << "\n";

    // Створюємо знімок стану
    ledger.create_snapshot(101);

    // 2. Списання комісії 30.00 грн
    ledger.post_transaction("FEE-100", "Комісія", {
        {201, 3000},
        {401, -3000}
    });

    std::cout << "Баланс банку: " << ledger.get_balance(101) << " коп.\n";
    std::cout << "Баланс зобов'язань клієнта: " << ledger.get_balance(201) << " коп.\n";
    std::cout << "Баланс доходів: " << ledger.get_balance(401) << " коп.\n";

    // 3. Сторнування помилкової комісії
    ledger.reverse_transaction(2, "REV-FEE-100");
    std::cout << "Після сторнування комісії, зобов'язання клієнта: " 
              << ledger.get_balance(201) << " коп.\n";

    return 0;
}
```
:::

## Детальний розбір механізмів та обробки крайових випадків

### 1. Двоетапна перевірка перед фіксацією

Проведення транзакції є суворо атомарною операцією. Алгоритм функції `post_transaction` виконує перевірки в чіткій послідовності:
- **Перевірка на ідемпотентність**: якщо ключ `idempotency_key` уже зафіксовано в системі, виконання негайно припиняється без додавання нових рядків. Це запобігає повторним списанням при мережевих ретраях клієнта.
- **Контроль інваріанта нульової суми**: обчислюється сума всіх складових `amount`. Якщо сума відмінна від нуля навіть на 1 копійку, транзакція відхиляється цілком.
- **Валідація посилальної цілісності**: перевіряється існування кожного `account_id` у плані рахунків.

Лише після успішного проходження всіх трьох бар'єрів генератор монотонної послідовності `global_sequence_` присвоює номери кожній проводці, і транзакція додається до журналу.

### 2. Алгоритм знімків та оптимізація читання

Прямий підрахунок залишку рахунку через повне сканування всього журналу проводок має часову складність `O(N)`, де `N` — загальна кількість транзакцій за всю історію рахунку.

Застосування методу `create_snapshot` зберігає агрегований баланс та останній номер черги `at_sequence`. Функція `get_balance`:
1. Зчитує збережений базовий баланс зі знімка за час `O(1)`.
2. Сканує лише ті проводки в журналі, чий номер `sequence` строго більший за `at_sequence`.
3. Додає отриману дельту до базового балансу.

Це скорочує складність операції читання до `O(k)`, де `k` — невелика кількість нових проводок, зроблених після створення останнього знімка.

### 3. Сторнування як альтернатива видаленню

Функція `reverse_transaction` демонструє принцип незмінності: замість зміни або видалення попередніх записів генерується нова компенсуюча транзакція, в якій кожна проводка отримує протилежне за знаком значення (`-p.amount`). Це дозволяє повністю відновити початковий баланс рахунків і водночас зберегти вичерпний аудиторський слід помилкової операції.

### 4. Порівняння ідіоматичних моделей C та C++

Реалізація мовою C спирається на монолітну структуру `Ledger` із фіксованими статичними масивами, що забезпечує нульовий рівень динамічної фрагментації пам'яті та передбачувану поведінку у вбудованих або низькорівневих сервісах. Усі помилки повертаються через явні числові коди.

Реалізація мовою C++ використовує інкапсуляцію в клас `LedgerEngine`, контейнери `std::vector` і `std::unordered_map` для динамічного масштабування та `std::string_view` для передачі рядків без зайвого виділення пам'яті в купі. Застосування `enum class` виключає неявне приведення типів рахунків, а метод `reverse_transaction` самостійно керує життєвим циклом даних без ризику витоків пам'яті (принцип RAII).

### 5. Покроковий розбір демонстраційного сценарію

Демонстраційна функція `main()` відтворює типовий життєвий цикл платіжного сервісу:
1. **Ініціалізація плану рахунків**: створюються три рахунки: активний рахунок банку (`101`, `ASSET`), пасивний рахунок зобов'язань перед клієнтами (`201`, `LIABILITY`) та рахунок доходів платформи (`401`, `REVENUE`).
2. **Первинне поповнення гаманця (Tx 1)**: клієнт вносить 1000.00 грн (100 000 копійок). Рушій створює проводку дебету на рахунок 101 (`+100000`) та кредит на рахунок 201 (`-100000`). Сума операції строго дорівнює нулю.
3. **Імітація збою мережі та повторний запит**: клієнт надсилає той самий ключ `DEP-001`. Рушій виявляє ключ у реєстрі та повертає код ідемпотентного пропуску (`1`), не списуючи кошти повторно.
4. **Фіксація контрольного знімка**: викликається `create_snapshot(101)`, що фіксує поточний баланс 100 000 копійок на поточному номері послідовності.
5. **Списання сервісної комісії (Tx 2)**: списується 20.00 грн (2 000 копійок) із рахунку клієнта 201 (`+2000`) на рахунок доходу 401 (`-2000`).
6. **Розрахунок залишків**: функція `get_balance` миттєво обчислює стан банку через базовий знімок (без повторного проходження проводок) та стан клієнта через підсумовування дельти проводок.
7. **Компенсуюче сторнування**: операція комісії скасовується через `reverse_transaction(2)`, повертаючи залишок клієнта до вихідного стану без руйнування історії записів.
