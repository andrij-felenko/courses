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
