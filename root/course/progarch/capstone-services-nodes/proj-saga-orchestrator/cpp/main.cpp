#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <chrono>
#include <expected>
#include <stdexcept>

namespace payflow::saga {

enum class SagaStatus {
    Pending,
    Succeeded,
    Failed,
    Compensated
};

struct ChargeSagaState {
    std::string charge_id;
    std::string merchant_id;
    std::string idempotency_key;
    int64_t amount_cents;
    std::string currency;
    SagaStatus status;
};

struct OutboxRecord {
    std::string event_id;
    std::string event_type;
    std::string payload_json;
    std::chrono::system_clock::time_point created_at;
};

// RAII обгортка бази даних для гарантії атомарного завершення транзакції
class DbTransaction {
public:
    explicit DbTransaction() : committed_(false) {
        std::cout << "[DB] BEGIN LOCAL ACID TRANSACTION\n";
    }
    
    ~DbTransaction() {
        if (!committed_) {
            std::cout << "[DB] ROLLBACK TRANSACTION (RAII Safe Guard)\n";
        }
    }

    void execute(const std::string& query) {
        std::cout << "[DB EXEC] " << query << "\n";
    }

    void commit() {
        std::cout << "[DB] COMMIT TRANSACTION SUCCESSFUL\n";
        committed_ = true;
    }

    // Заборона копіювання транзакційного об'єкта
    DbTransaction(const DbTransaction&) = delete;
    DbTransaction& operator=(const DbTransaction&) = delete;

private:
    bool committed_;
};

class PaymentSagaOrchestrator {
public:
    // Повертає std::expected (C++23) для явною обробки помилок без винятків
    std::expected<void, std::string> commit_saga_with_outbox(const ChargeSagaState& saga) {
        try {
            DbTransaction tx;

            // 1. Запис стану саги
            std::string status_str = (saga.status == SagaStatus::Succeeded) ? "SUCCEEDED" : "FAILED";
            std::string charge_sql = "INSERT INTO charges (id, merchant_id, idempotency_key, amount_cents, status) "
                                     "VALUES ('" + saga.charge_id + "', '" + saga.merchant_id + "', '" + 
                                     saga.idempotency_key + "', " + std::to_string(saga.amount_cents) + ", '" + status_str + "')";
            tx.execute(charge_sql);

            // 2. Атомарний запис у таблицю outbox
            std::string event_type = (saga.status == SagaStatus::Succeeded) ? "charge.succeeded" : "charge.failed";
            std::string outbox_sql = "INSERT INTO outbox_events (event_type, payload) VALUES ('" + 
                                     event_type + "', '{\"charge_id\":\"" + saga.charge_id + "\"}')";
            tx.execute(outbox_sql);

            // 3. Фіксація змін
            tx.commit();
            return {};
        } catch (const std::exception& e) {
            return std::unexpected(std::string("Database ACID failure: ") + e.what());
        }
    }
};

} // namespace payflow::saga
