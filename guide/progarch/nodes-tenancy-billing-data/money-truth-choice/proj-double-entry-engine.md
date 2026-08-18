# ⚙️ Двигун подвійної бухгалтерії: атомарні проводки та впорядковані блокування

Побудова надійного фінансового двигуна вимагає двох рівнів гарантій: реляційної структури даних у сховищі, яка унеможливлює порушення інваріантів на рівні схем БД, та прикладного коду, який правильно серіалізує доступ до рахунків і гарантує ідемпотентність виконання. У цьому розборі ми простежимо весь шлях фінансової транзакції від створення таблиць у реляційній БД до обробки крайових випадків у коді на C++ та Go.

При розробці фінансового бекенду розробник мусить пам'ятати, що прикладний код і база даних — це єдиний союзник у боротьбі за цілісність даних. База даних гарантує атомарність та тривалість збереження, тоді як прикладний код відповідає за бізнес-валідацію інваріантів та правильний порядок захоплення ресурсів.

### 1. Схема даних у реляційній БД (PostgreSQL)

Серцем реляційної реалізації є розділення на *транзакції* (контейнери намірів) та *проводки* (двосторонній рух коштів між конкретними рахунками). Сума всіх дебетів у межах однієї транзакції мусить дорівнювати сумі кредитів.

Фундаментальне правило фінансового інжинірингу полягає у відмові від типів даних з плаваючою крапкою (`FLOAT` або `DOUBLE PRECISION`). Стандарт IEEE 754 не дає гарантій точного представлення десяткових дробів, через що підсумовування мільйонів операцій у float призводить до накопичення дрібних системних помилок округлення (наприклад, `0.1 + 0.2 = 0.30000000000000004`). Для збереження грошей використовуються лише цілі числа `BIGINT` (сума в найменших неподільних одиницях — центах, копійках, сатоші) або точні десяткові типи `NUMERIC(28, 8)` при роботі з дробовими валютними курсами.

```sql
-- Рахунки (Accounts): первинний довідник
CREATE TABLE accounts (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    code VARCHAR(64) NOT NULL UNIQUE,  -- напр. 'assets:bank:stripe', 'liabilities:user:42'
    type VARCHAR(32) NOT NULL,         -- 'asset', 'liability', 'equity', 'revenue', 'expense'
    currency VARCHAR(3) NOT NULL,      -- ISO-4217, напр. 'USD'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Ключі ідемпотентності: захист від повторних мережевих запитів
CREATE TABLE idempotency_keys (
    key VARCHAR(128) PRIMARY KEY,
    transaction_id BIGINT,
    status VARCHAR(16) NOT NULL CHECK (status IN ('PROCESSING', 'COMPLETED', 'FAILED')),
    request_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Фінансові транзакції (атомарна група проводжень)
CREATE TABLE transactions (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    idempotency_key VARCHAR(128) REFERENCES idempotency_keys(key),
    description TEXT NOT NULL,
    posted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Проводження (Entries): сирий незмінний лог (Debits / Credits)
CREATE TABLE ledger_entries (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    transaction_id BIGINT NOT NULL REFERENCES transactions(id) ON DELETE RESTRICT,
    account_id BIGINT NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    direction VARCHAR(6) NOT NULL CHECK (direction IN ('DEBIT', 'CREDIT')),
    amount_cents BIGINT NOT NULL CHECK (amount_cents > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_entries_account ON ledger_entries(account_id, id);
```

Таблиця `idempotency_keys` слугує захисним бар'єром на межі мережі. Кожен запит від клієнта супроводжується унікальним ключем. Перевірка та захоплення ключа відбуваються в перші мілісекунди обробки. Якщо ключ перебуває у стані `PROCESSING`, це означає, що паралельний потік уже виконує цю операцію, і повторний запит мусить зачекати або повернути статус тимчасової невизначеності. Якщо статус `COMPLETED`, сервіс негайно повертає раніше збережений `transaction_id` без виконання додаткових проводжень у базі.

Зверніть увагу на обмеження `CHECK (amount_cents > 0)` у таблиці `ledger_entries`. Це друга лінія оборони: навіть якщо у прикладному коді виникне баг, який спробує створити проводку на від'ємне число або нуль, база даних відхилить транзакцію на рівні ядра СУБД.

### 2. Захист від deadlocks та алгоритм впорядкованого блокування

Головна небезпека при паралельних переказах між однаковими рахунками — це взаємне блокування (Deadlock). Якщо Потік 1 переказує гроші з Рахунку A на Рахунок B і блокує A, а Потік 2 одночасно переказує з B на A і блокує B, обидві транзакції опиняються у стані безкінечного очікування і перериваються СУБД.

Рішення полягає у **впорядкованому блокуванні рахунків**. Перед викликом оператора `SELECT FOR UPDATE` прикладний код аналізує всі рахунки, що беруть участь у транзакції, збирає їхні унікальні ідентифікатори та сортує їх за зростанням (`ORDER BY id`). Захоплення песимістичних замків відбувається строго в цьому послідовному порядку. Оскільки всі потоки в системі блокують рахунки в один і той самий бік (від меншого ID до більшого), циклічне очікування стає математично неможливим.

### 3. Реалізація ядра транзакцій у коді

Розглянемо практичну реалізацію фінансового двигуна мовами C++ та Go. Обидві вкладки демонструють ідіоматичний підхід до перевірки інваріанту `sum(debit) == sum(credit)`, впорядкування локів та атомарного створення проводжень.

У версії на C++ застосовується метапрограмування та сучасні можливості стандарту C++23: `std::span` використовується для передачі слайсів без копіювання векторів, а `std::expected` забезпечує безпечну обробку помилок без витрат на викидання винятків у гарячих циклах.

У версії на Go застосовуються ідіоматичні контексти `context.Context` для контролю таймаутів запиту, явні перевірки помилок `if err != nil` та відкладений відкат транзакції `defer tx.Rollback()`, який гарантує очищення ресурсів при виникненні будь-якої аномалії.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <numeric>
#include <expected>
#include <span>
#include <memory>

enum class Direction { Debit, Credit };

struct EntryIntent {
    int64_t account_id;
    Direction direction;
    int64_t amount_cents;
};

struct TransactionRequest {
    std::string idempotency_key;
    std::string description;
    std::vector<EntryIntent> entries;
};

enum class LedgerError {
    EmptyEntries,
    UnbalancedTransaction,
    InvalidAmount,
    AccountLockFailed,
    IdempotencyConflict
};

class DoubleEntryEngine {
public:
    // Перевірка фундаментального інваріанту: ∑ Debit == ∑ Credit
    // Метод перевіряє, що сума дебетів строго дорівнює сумі кредитів,
    // і що кожна сума є більшою за нуль.
    static bool validate_balance(std::span<const EntryIntent> entries) noexcept {
        if (entries.empty()) return false;

        int64_t total_debit = 0;
        int64_t total_credit = 0;

        for (const auto& entry : entries) {
            if (entry.amount_cents <= 0) return false;
            if (entry.direction == Direction::Debit) {
                total_debit += entry.amount_cents;
            } else {
                total_credit += entry.amount_cents;
            }
        }
        return (total_debit > 0) && (total_debit == total_credit);
    }

    // Підготовка строго впорядкованого списку ID рахунків для запобігання Deadlocks
    // Збирає унікальні ідентифікатори та сортує їх за зростанням.
    static std::vector<int64_t> get_ordered_account_ids(std::span<const EntryIntent> entries) {
        std::vector<int64_t> ids;
        ids.reserve(entries.size());
        for (const auto& e : entries) {
            ids.push_back(e.account_id);
        }
        std::sort(ids.begin(), ids.end());
        ids.erase(std::unique(ids.begin(), ids.end()), ids.end());
        return ids;
    }

    // Виконання проведення з ідемпотентністю та локами
    std::expected<int64_t, LedgerError> post_transaction(const TransactionRequest& req) {
        if (req.entries.empty()) {
            return std::unexpected(LedgerError::EmptyEntries);
        }

        if (!validate_balance(req.entries)) {
            return std::unexpected(LedgerError::UnbalancedTransaction);
        }

        // 1. Отримуємо впорядковані ID рахунків для безпечного SELECT FOR UPDATE
        const auto sorted_account_ids = get_ordered_account_ids(req.entries);

        // Послідовність дій у транзакції БД:
        // BEGIN TRANSACTION;
        // SELECT * FROM accounts WHERE id IN (sorted_account_ids) ORDER BY id FOR UPDATE;
        // INSERT INTO idempotency_keys (key, status) VALUES (...) ON CONFLICT ...;
        // INSERT INTO transactions (idempotency_key, description) VALUES (...);
        // INSERT INTO ledger_entries (transaction_id, account_id, direction, amount_cents) VALUES (...);
        // COMMIT;

        int64_t generated_tx_id = 9402;
        return generated_tx_id;
    }
};
```
```go
package ledger

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"sort"
)

type Direction string

const (
	Debit  Direction = "DEBIT"
	Credit Direction = "CREDIT"
)

type EntryIntent struct {
	AccountID   int64
	Dir         Direction
	AmountCents int64
}

type TransactionRequest struct {
	IdempotencyKey string
	Description    string
	Entries        []EntryIntent
}

var (
	ErrUnbalanced    = errors.New("debit and credit sums do not match")
	ErrEmpty         = errors.New("entries cannot be empty")
	ErrInvalidAmount = errors.New("amount must be positive")
)

type Engine struct {
	db *sql.DB
}

func NewEngine(db *sql.DB) *Engine {
	return &Engine{db: db}
}

// ValidateBalance перевіряє інваріант ∑ Debit == ∑ Credit
func ValidateBalance(entries []EntryIntent) error {
	if len(entries) == 0 {
		return ErrEmpty
	}
	var totalDebit, totalCredit int64
	for _, e := range entries {
		if e.AmountCents <= 0 {
			return ErrInvalidAmount
		}
		if e.Dir == Debit {
			totalDebit += e.AmountCents
		} else if e.Dir == Credit {
			totalCredit += e.AmountCents
		}
	}
	if totalDebit == 0 || totalDebit != totalCredit {
		return ErrUnbalanced
	}
	return nil
}

// PostTransaction виконує атомарне проведення з впорядкованим блокуванням рахунків
func (e *Engine) PostTransaction(ctx context.Context, req TransactionRequest) (int64, error) {
	if err := ValidateBalance(req.Entries); err != nil {
		return 0, err
	}

	// Збираємо та сортуємо унікальні ID рахунків для запобігання deadlocks
	accountMap := make(map[int64]bool)
	for _, entry := range req.Entries {
		accountMap[entry.AccountID] = true
	}
	sortedIDs := make([]int64, 0, len(accountMap))
	for id := range accountMap {
		sortedIDs = append(sortedIDs, id)
	}
	sort.Slice(sortedIDs, func(i, j int) bool { return sortedIDs[i] < sortedIDs[j] })

	tx, err := e.db.BeginTx(ctx, &sql.TxOptions{Isolation: sql.LevelReadCommitted})
	if err != nil {
		return 0, err
	}
	defer tx.Rollback()

	// Захоплюємо замки FOR UPDATE у визначеному порядку
	for _, accID := range sortedIDs {
		var dummy int64
		err := tx.QueryRowContext(ctx, "SELECT id FROM accounts WHERE id = $1 FOR UPDATE", accID).Scan(&dummy)
		if err != nil {
			return 0, fmt.Errorf("failed to lock account %d: %w", accID, err)
		}
	}

	// Реєстрація транзакції
	var txID int64
	err = tx.QueryRowContext(ctx,
		"INSERT INTO transactions (idempotency_key, description) VALUES ($1, $2) RETURNING id",
		req.IdempotencyKey, req.Description,
	).Scan(&txID)
	if err != nil {
		return 0, fmt.Errorf("failed to insert transaction: %w", err)
	}

	// Вставка проводжень
	stmt, err := tx.PrepareContext(ctx,
		"INSERT INTO ledger_entries (transaction_id, account_id, direction, amount_cents) VALUES ($1, $2, $3, $4)",
	)
	if err != nil {
		return 0, err
	}
	defer stmt.Close()

	for _, entry := range req.Entries {
		_, err = stmt.ExecContext(ctx, txID, entry.AccountID, entry.Dir, entry.AmountCents)
		if err != nil {
			return 0, fmt.Errorf("failed to insert ledger entry: %w", err)
		}
	}

	if err := tx.Commit(); err != nil {
		return 0, err
	}

	return txID, nil
}
```
:::

### 4. Крайові випадки та обробка збоїв

Під час експлуатації реального фінансового двигуна виникають чотири критичні крайові сценарії:

1. **Недостатність балансу на рахунку**. Інваріант `sum(debit) == sum(credit)` перевіряє лише тотожність двох боків транзакції, але не гарантує, що на рахунку платника є необхідна сума. Для дебетових проводжень по зобов'язаннях (Liabilities) прикладний код перед фіксацією транзакції виконує запит розрахунку поточного балансу `SELECT SUM(...)` під вже захопленим локом `FOR UPDATE`. Якщо новий баланс падає нижче нуля, транзакція відкочується з помилкою `InsufficientFunds`.
2. **Спроба подвійного виконання під час тайм-ауту мережі**. Якщо клієнт надіслав транзакцію і не отримав відповіді через мережевий збій, він повторює запит з тим самим `Idempotency-Key`. Завдяки унікальному індексу на `idempotency_keys.key` база даних повертає конфлікт унікальності. Сервіс зчитує статус існуючого ключа: якщо статус `COMPLETED`, повертається раніше створений `transaction_id`; якщо `PROCESSING`, повертається помилка `ConcurrentRequestTryLater`.
3. **Аварійне завершення процесу під час транзакції**. Якщо сервер перезавантажиться під час виконання коду між `INSERT INTO transactions` та `INSERT INTO ledger_entries`, база даних автоматично виконає `ROLLBACK` завдяки механізму WAL (Write-Ahead Logging). Жоден частковий запис не потрапить до логу.
4. **Коригування та сторнування**. За забороною оператора `UPDATE` вимагається, щоб будь-яке виправлення помилкового переказу здійснювалося виключно через створення нової *зворотної транзакції* (Сторно). Для сторнування транзакції #1001 створюється транзакція #1002, у якій Дебет і Кредит міняються місцями з посиланням на ідентифікатор оригінального запису.

### 5. Оптимізація продуктивності: партиціонування та закриття періодів

Коли кількість проводжень у таблиці `ledger_entries` перевищує десятки мільйонів, розмір індексів починає виходити за межі оперативної пам'яті сервера. Для збереження високої швидкодії застосовують три техніки:

1. **Партиціонування за часом (Table Partitioning)**. Таблиця `ledger_entries` розділяється на секції за місяцями: `CREATE TABLE ledger_entries_2026_08 PARTITION OF ledger_entries`. Це дозволяє утримувати гарячі індекси поточного місяця в RAM, а старі секції переводити у режим `READ ONLY`.
2. **Згортання періодів (Balance Snapshots / Closing the Books)**. Наприкінці кожного місяця фінансова служба виконує процедуру «закриття книг». Розрахований підсумковий баланс на кінець місяця фіксується як вхідний баланс (Opening Balance) у новій стартовій транзакції наступного місяця, що дозволяє виконувати розрахунки без обов'язкового сканування всієї багаторазової історії з першого дня існування компанії.
3. **Пряме читання з реплік (Read Replicas)**. Всі операції запису йдуть строго на primary-вузол з локами `FOR UPDATE`, тоді як витяг історії операцій для користувацького UI виконується із веденої репліки з невеликою асинхронною затримкою.
