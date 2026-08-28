// C++20: Idiomatic RAII Transaction & Outbox Repository
#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <chrono>

enum class TxError {
    DatabaseConnectionFailed,
    InsufficientFunds,
    OutboxWriteFailed,
    TransactionAborted
};

struct OutboxEvent {
    std::string event_id;
    std::string aggregate_type;
    std::string aggregate_id;
    std::string event_type;
    std::string payload_json;
};

// Мок-адаптер бази даних з підтримкою RAII-транзакцій
class DbConnection {
public:
    void begin_transaction() {
        std::cout << "[DB] BEGIN TRANSACTION;\n";
        in_tx_ = true;
    }
    
    void commit() {
        if (in_tx_) {
            std::cout << "[DB] COMMIT;\n";
            in_tx_ = false;
        }
    }
    
    void rollback() {
        if (in_tx_) {
            std::cout << "[DB] ROLLBACK;\n";
            in_tx_ = false;
        }
    }
    
    bool is_in_transaction() const { return in_tx_; }
    
    bool execute_sql(std::string_view query) {
        std::cout << "[DB EXEC] " << query << "\n";
        return true;
    }

private:
    bool in_tx_{false};
};

// RAII обгортка для безпечного управління транзакцією
class ScopedTransaction {
public:
    explicit ScopedTransaction(DbConnection& db) : db_(db) {
        db_.begin_transaction();
    }
    
    ~ScopedTransaction() {
        if (!committed_ && db_.is_in_transaction()) {
            db_.rollback();
        }
    }
    
    void commit() {
        db_.commit();
        committed_ = true;
    }

    ScopedTransaction(const ScopedTransaction&) = delete;
    ScopedTransaction& operator=(const ScopedTransaction&) = delete;

private:
    DbConnection& db_;
    bool committed_{false};
};

class WalletRepository {
public:
    explicit WalletRepository(DbConnection& db) : db_(db) {}

    std::expected<void, TxError> transfer_and_publish_outbox(
        std::string_view sender_id,
        std::string_view receiver_id,
        int64_t amount_cents,
        const OutboxEvent& event
    ) {
        ScopedTransaction tx(db_);

        // 1. Перевірка інваріанту та оновлення балансу відправника
        std::string update_sender = "UPDATE wallet_accounts SET balance_cents = balance_cents - " +
            std::to_string(amount_cents) + " WHERE account_id = '" + std::string(sender_id) + "'";
        if (!db_.execute_sql(update_sender)) {
            return std::unexpected(TxError::InsufficientFunds);
        }

        // 2. Поповнення балансу отримувача
        std::string update_receiver = "UPDATE wallet_accounts SET balance_cents = balance_cents + " +
            std::to_string(amount_cents) + " WHERE account_id = '" + std::string(receiver_id) + "'";
        if (!db_.execute_sql(update_receiver)) {
            return std::unexpected(TxError::TransactionAborted);
        }

        // 3. Запис події у таблицю outbox_events у цій же транзакції
        std::string insert_outbox = "INSERT INTO outbox_events (event_id, aggregate_type, aggregate_id, event_type, payload_json) VALUES ('" +
            event.event_id + "', '" + event.aggregate_type + "', '" + event.aggregate_id + "', '" +
            event.event_type + "', '" + event.payload_json + "')";
        if (!db_.execute_sql(insert_outbox)) {
            return std::unexpected(TxError::OutboxWriteFailed);
        }

        tx.commit();
        return {};
    }

private:
    DbConnection& db_;
};
