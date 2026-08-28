#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <memory>
#include <optional>
#include <expected>
#include <mutex>
#include <unordered_map>
#include <format>

// Перелік станів повідомлення у вхідній скриньці
enum class InboxStatus {
    Received,
    Processing,
    Processed,
    Failed
};

// Структура вхідного повідомлення
struct InboxMessage {
    std::string message_id;
    std::string event_type;
    std::string payload;
    InboxStatus status{InboxStatus::Received};
    int retry_count{0};
    int max_retries{5};
    std::chrono::system_clock::time_point locked_until{};
    std::string locked_by{};
    std::chrono::system_clock::time_point created_at{std::chrono::system_clock::now()};
    std::optional<std::chrono::system_clock::time_point> processed_at{std::nullopt};
    std::optional<std::string> last_error{std::nullopt};
};

// Імітація транзакційного сховища (на практиці — PostgreSQL / SQLite)
class TransactionalDatabase {
public:
    struct AccountState {
        int64_t user_id;
        double balance;
    };

    // Початок транзакції
    class Transaction {
    public:
        Transaction(TransactionalDatabase& db) : db_(db), committed_(false) {
            db_.lock();
        }

        ~Transaction() {
            if (!committed_) {
                rollback();
            }
            db_.unlock();
        }

        // 1. Атомарне резервування або перевірка унікальності в inbox
        bool try_insert_or_acquire_inbox(const std::string& msg_id, 
                                         const std::string& event_type, 
                                         const std::string& payload,
                                         std::string_view worker_id,
                                         std::chrono::seconds lease_duration) {
            auto it = db_.inbox_table_.find(msg_id);
            auto now = std::chrono::system_clock::now();

            if (it == db_.inbox_table_.end()) {
                // Нове повідомлення — вставляємо одразу в стані Processing
                InboxMessage msg;
                msg.message_id = msg_id;
                msg.event_type = event_type;
                msg.payload = payload;
                msg.status = InboxStatus::Processing;
                msg.locked_until = now + lease_duration;
                msg.locked_by = std::string(worker_id);
                staged_inbox_inserts_[msg_id] = msg;
                return true;
            }

            // Повідомлення вже є
            if (it->second.status == InboxStatus::Processed) {
                // Уже успішно оброблено — дублікат відхиляється
                return false;
            }

            if (it->second.status == InboxStatus::Processing && it->second.locked_until > now) {
                // Обробляється іншим активним воркером
                return false;
            }

            // Повідомлення очікує або ліза попереднього воркера спливла
            InboxMessage updated = it->second;
            updated.status = InboxStatus::Processing;
            updated.locked_until = now + lease_duration;
            updated.locked_by = std::string(worker_id);
            staged_inbox_updates_[msg_id] = updated;
            return true;
        }

        // 2. Бізнес-операція: модифікація балансу
        void update_balance(int64_t user_id, double delta) {
            double current = db_.accounts_[user_id].balance;
            staged_balances_[user_id] = current + delta;
        }

        // 3. Успішне завершення обробки
        void mark_processed(const std::string& msg_id) {
            staged_processed_ids_.push_back(msg_id);
        }

        // 4. Фіксація помилки обробки
        void mark_failed(const std::string& msg_id, std::string_view error_msg) {
            staged_errors_[msg_id] = std::string(error_msg);
        }

        void commit() {
            // Застосовуємо всі підготовлені мутації
            for (auto& [id, msg] : staged_inbox_inserts_) {
                db_.inbox_table_[id] = msg;
            }
            for (auto& [id, msg] : staged_inbox_updates_) {
                db_.inbox_table_[id] = msg;
            }
            for (auto& [user_id, balance] : staged_balances_) {
                db_.accounts_[user_id] = {user_id, balance};
            }
            auto now = std::chrono::system_clock::now();
            for (const auto& id : staged_processed_ids_) {
                db_.inbox_table_[id].status = InboxStatus::Processed;
                db_.inbox_table_[id].processed_at = now;
                db_.inbox_table_[id].locked_by.clear();
            }
            for (auto& [id, err] : staged_errors_) {
                auto& msg = db_.inbox_table_[id];
                msg.retry_count++;
                msg.last_error = err;
                if (msg.retry_count >= msg.max_retries) {
                    msg.status = InboxStatus::Failed;
                } else {
                    msg.status = InboxStatus::Received; // повертаємо для повтору
                }
                msg.locked_by.clear();
            }
            committed_ = true;
        }

        void rollback() {
            staged_inbox_inserts_.clear();
            staged_inbox_updates_.clear();
            staged_balances_.clear();
            staged_processed_ids_.clear();
            staged_errors_.clear();
        }

    private:
        TransactionalDatabase& db_;
        bool committed_;
        std::unordered_map<std::string, InboxMessage> staged_inbox_inserts_;
        std::unordered_map<std::string, InboxMessage> staged_inbox_updates_;
        std::unordered_map<int64_t, double> staged_balances_;
        std::vector<std::string> staged_processed_ids_;
        std::unordered_map<std::string, std::string> staged_errors_;
    };

    std::unique_ptr<Transaction> begin_transaction() {
        return std::make_unique<Transaction>(*this);
    }

    double get_balance(int64_t user_id) {
        std::lock_guard<std::mutex> lock(mutex_);
        return accounts_[user_id].balance;
    }

    bool is_processed(const std::string& msg_id) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = inbox_table_.find(msg_id);
        return it != inbox_table_.end() && it->second.status == InboxStatus::Processed;
    }

private:
    void lock() { mutex_.lock(); }
    void unlock() { mutex_.unlock(); }

    std::mutex mutex_;
    std::unordered_map<std::string, InboxMessage> inbox_table_;
    std::unordered_map<int64_t, AccountState> accounts_;
};

// Сервіс обробника вхідних повідомлень
class InboxConsumer {
public:
    InboxConsumer(TransactionalDatabase& db, std::string worker_id)
        : db_(db), worker_id_(std::move(worker_id)) {}

    // Обробка вхідного повідомлення з гарантією дедуплікації
    enum class ProcessOutcome {
        Success,
        DuplicateIgnored,
        TransientFailure,
        TerminalFailure
    };

    ProcessOutcome handle_payment_event(const std::string& msg_id, 
                                         int64_t user_id, 
                                         double amount) {
        auto tx = db_.begin_transaction();

        // 1. Атомарне захоплення повідомлення
        bool acquired = tx->try_insert_or_acquire_inbox(
            msg_id, "PaymentReceived", std::to_string(amount), worker_id_, std::chrono::seconds(30)
        );

        if (!acquired) {
            // Дубль або повідомлення зайняте іншим воркером
            return ProcessOutcome::DuplicateIgnored;
        }

        // 2. Виконання бізнес-логіки
        if (amount <= 0.0) {
            // Некоректні вхідні дані — термінальна помилка
            tx->mark_failed(msg_id, "Сума платежу повинна бути додатною");
            tx->commit();
            return ProcessOutcome::TerminalFailure;
        }

        try {
            // Зміна стану балансу
            tx->update_balance(user_id, amount);

            // 3. Позначення повідомлення обробленим у тій самій транзакції
            tx->mark_processed(msg_id);

            // 4. Фіксація транзакції
            tx->commit();
            return ProcessOutcome::Success;

        } catch (const std::exception& ex) {
            tx->rollback();
            
            // Відкриваємо окрему транзакцію для фіксації помилки
            auto err_tx = db_.begin_transaction();
            err_tx->mark_failed(msg_id, ex.what());
            err_tx->commit();
            return ProcessOutcome::TransientFailure;
        }
    }

private:
    TransactionalDatabase& db_;
    std::string worker_id_;
};

int main() {
    TransactionalDatabase db;
    InboxConsumer worker1(db, "worker-node-1");
    InboxConsumer worker2(db, "worker-node-2");

    int64_t user = 42;
    std::string msg1 = "evt-pay-1001";

    std::cout << "[Крок 1] Первинна обробка повідомлення " << msg1 << "\n";
    auto res1 = worker1.handle_payment_event(msg1, user, 250.0);
    std::cout << "Результат: " << (res1 == InboxConsumer::ProcessOutcome::Success ? "Успіх" : "Збій") << "\n";
    std::cout << "Поточний баланс: " << db.get_balance(user) << " грн\n\n";

    std::cout << "[Крок 2] Брокер повторно надсилає дублікат " << msg1 << "\n";
    auto res2 = worker2.handle_payment_event(msg1, user, 250.0);
    std::cout << "Результат: " << (res2 == InboxConsumer::ProcessOutcome::DuplicateIgnored ? "Дублікат безпечно проігноровано" : "Помилка") << "\n";
    std::cout << "Баланс після повтору (захищено від дубля): " << db.get_balance(user) << " грн\n";

    return 0;
}
