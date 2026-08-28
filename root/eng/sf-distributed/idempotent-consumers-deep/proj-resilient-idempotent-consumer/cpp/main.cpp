#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <unordered_map>
#include <shared_mutex>
#include <chrono>
#include <sstream>
#include <iomanip>
#include <expected>
#include <stdexcept>

// Повідомлення з брокера
struct Message {
    std::string id;
    std::string topic;
    int partition{0};
    int64_t offset{0};
    std::string payload;
    int attempt{1};
};

enum class ProcessingStatus {
    Pending,
    InProgress,
    Completed,
    Quarantined
};

// Результат операції
enum class ConsumerError {
    DatabaseError,
    ExternalApiError,
    PoisonMessageQuarantined
};

class ResilientIdempotentConsumer {
public:
    explicit ResilientIdempotentConsumer(int max_attempts = 3)
        : max_attempts_(max_attempts), lease_duration_(std::chrono::seconds(30)) {}

    // Детермінований токен для зовнішніх API
    std::string derive_outbound_key(std::string_view msg_id, std::string_view action) const {
        std::hash<std::string_view> hasher;
        size_t h1 = hasher(msg_id);
        size_t h2 = hasher(action);
        std::stringstream ss;
        ss << "idemp_" << std::hex << h1 << "_" << h2;
        return ss.str();
    }

    // Трифазна обробка
    std::expected<void, ConsumerError> process_message(const Message& msg) {
        // 0. Перевірка швидкого L1 кешу в пам'яті
        {
            std::shared_lock lock(cache_mutex_);
            if (completed_cache_.contains(msg.id)) {
                return {}; // Ідемпотентний пропуск
            }
        }

        const std::string outbound_key = derive_outbound_key(msg.id, "charge_payment");

        // ФАЗА 1: Локальна фіксація наміру (Inbox DB)
        auto phase1_res = reserve_inbox_intent(msg, outbound_key);
        if (!phase1_res) {
            return std::unexpected(ConsumerError::DatabaseError);
        }

        if (*phase1_res == ProcessingStatus::Completed) {
            mark_local_cache(msg.id);
            return {};
        }

        if (*phase1_res == ProcessingStatus::Quarantined) {
            route_to_dlq(msg, "Перевищено ліміт спроб обробки");
            return {}; // Підтверджуємо зсув, черга розблокована
        }

        // ФАЗА 2: Виклик стороннього API з токеном ідемпотентності
        auto side_effect_res = call_external_payment_api(outbound_key, msg.payload);
        if (!side_effect_res) {
            return std::unexpected(ConsumerError::ExternalApiError);
        }

        // ФАЗА 3: Фіналізація стану в БД
        if (!finalize_inbox_transaction(msg.id, *side_effect_res)) {
            return std::unexpected(ConsumerError::DatabaseError);
        }

        mark_local_cache(msg.id);
        return {};
    }

private:
    std::expected<ProcessingStatus, ConsumerError> reserve_inbox_intent(const Message& msg, const std::string& outbound_key) {
        // Емуляція атомарного запису в PostgreSQL Inbox
        std::unique_lock lock(db_mutex_);
        auto& entry = simulated_db_inbox_[msg.id];
        
        if (entry.status == ProcessingStatus::Completed) {
            return ProcessingStatus::Completed;
        }

        entry.attempts++;
        if (entry.attempts > max_attempts_) {
            entry.status = ProcessingStatus::Quarantined;
            return ProcessingStatus::Quarantined;
        }

        entry.status = ProcessingStatus::InProgress;
        entry.outbound_key = outbound_key;
        entry.lease_expiry = std::chrono::steady_clock::now() + lease_duration_;
        return ProcessingStatus::InProgress;
    }

    std::expected<std::string, ConsumerError> call_external_payment_api(const std::string& idemp_key, std::string_view payload) {
        // Емуляція HTTP POST з заголовком Idempotency-Key
        // Зовнішній сервіс за ключем idemp_key ніколи не подвоїть платіж
        return "charge_ch_774129";
    }

    bool finalize_inbox_transaction(const std::string& msg_id, const std::string& external_ref) {
        std::unique_lock lock(db_mutex_);
        auto it = simulated_db_inbox_.find(msg_id);
        if (it == simulated_db_inbox_.end()) return false;

        it->second.status = ProcessingStatus::Completed;
        it->second.external_ref = external_ref;
        return true;
    }

    void mark_local_cache(const std::string& id) {
        std::unique_lock lock(cache_mutex_);
        completed_cache_[id] = std::chrono::steady_clock::now();
    }

    void route_to_dlq(const Message& msg, std::string_view reason) {
        std::cout << "[DLQ] Повідомлення ID=" << msg.id << " ізольовано. Причина: " << reason << "\n";
    }

    struct InboxRecord {
        ProcessingStatus status{ProcessingStatus::Pending};
        int attempts{0};
        std::string outbound_key;
        std::string external_ref;
        std::chrono::steady_clock::time_point lease_expiry;
    };

    int max_attempts_;
    std::chrono::seconds lease_duration_;
    mutable std::shared_mutex cache_mutex_;
    std::unordered_map<std::string, std::chrono::steady_clock::time_point> completed_cache_;
    
    std::mutex db_mutex_;
    std::unordered_map<std::string, InboxRecord> simulated_db_inbox_;
};
