// C++20: Ідіоматичний Edge Filter та Domain Deduplication з RAII та std::unordered_map

#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <unordered_set>
#include <chrono>
#include <memory>
#include <optional>
#include <expected>

class EdgeDeduplicator {
public:
    using Clock = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;

    explicit EdgeDeduplicator(std::chrono::seconds default_ttl)
        : default_ttl_(default_ttl) {}

    // Повертає true, якщо запит унікальний і зареєстрований; false якщо це дублікат
    bool check_and_register(std::string_view key) {
        const auto now = Clock::now();
        cleanup_expired(now);

        auto it = cache_.find(std::string(key));
        if (it != cache_.end()) {
            if (it->second > now) {
                return false; // Запит є дублікатом у межах TTL вікна
            }
        }

        cache_[std::string(key)] = now + default_ttl_;
        return true;
    }

private:
    void cleanup_expired(TimePoint now) {
        for (auto it = cache_.begin(); it != cache_.end(); ) {
            if (it->second <= now) {
                it = cache_.erase(it);
            } else {
                ++it;
            }
        }
    }

    std::chrono::seconds default_ttl_;
    std::unordered_map<std::string, TimePoint> cache_;
};

enum class DomainError {
    DuplicateKeyInDatabase,
    DatabaseConnectionFailed
};

class DomainRepository {
public:
    std::expected<void, DomainError> process_order_atomically(std::string_view order_id, std::string_view key) {
        if (processed_keys_.contains(std::string(key))) {
            return std::unexpected(DomainError::DuplicateKeyInDatabase);
        }

        // Атомарна мутація в DB
        processed_keys_.insert(std::string(key));
        std::cout << "[Domain C++] Executed order " << order_id << " with key " << key << " inside DB transaction.\n";
        return {};
    }

private:
    std::unordered_set<std::string> processed_keys_;
};

int main() {
    EdgeDeduplicator edge_gateway(std::chrono::seconds(60));
    DomainRepository db_repo;

    const std::string idempotency_key = "IDEM-KEY-7721";

    auto handle_request = [&](std::string_view req_id) {
        std::cout << "Handling request " << req_id << "...\n";
        if (!edge_gateway.check_and_register(idempotency_key)) {
            std::cout << "  -> Rejected at GATEWAY BOUNDARY (Duplicate key in Redis/Memory)\n";
            return;
        }

        auto res = db_repo.process_order_atomically(req_id, idempotency_key);
        if (!res) {
            std::cout << "  -> Rejected at DOMAIN DB LEVEL (ACID Unique Constraint)\n";
        }
    };

    handle_request("REQ-1");
    handle_request("REQ-1-RETRY-1"); // Зрізається на межі

    return 0;
}
