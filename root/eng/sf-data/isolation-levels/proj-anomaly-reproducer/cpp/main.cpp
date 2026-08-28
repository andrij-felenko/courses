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
