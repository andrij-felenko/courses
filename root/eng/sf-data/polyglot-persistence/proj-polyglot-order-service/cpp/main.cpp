#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <sstream>
#include <optional>
#include <memory>
#include <chrono>

namespace polyglot {

struct Order {
    int id;
    std::string customer;
    double amount;
    std::string status;
    uint64_t version;
};

struct OutboxEvent {
    int event_id;
    int order_id;
    std::string event_type;
    std::string payload;
    uint64_t version;
    bool processed;
};

class PolyglotOrderCoordinator {
public:
    // 1. Командний бік (Command Side): Атомарна транзакція в первинну БД
    bool create_order(int order_id, const std::string& customer, double amount) {
        Order ord{order_id, customer, amount, "CREATED", 1};
        primary_db_[order_id] = ord;

        // Генерація події в Outbox
        std::ostringstream ss;
        ss << "{\"id\":" << order_id << ",\"customer\":\"" << customer << "\",\"amount\":" << amount << "}";
        
        outbox_.push_back({
            static_cast<int>(outbox_.size() + 1),
            order_id,
            "ORDER_CREATED",
            ss.str(),
            1,
            false
        });

        return true;
    }

    // 2. Асинхронний обробник Outbox (CDC імітація)
    void sync_projections() {
        for (auto& event : outbox_) {
            if (!event.processed) {
                // Синхронізація з Key-Value кешем з перевіркою версії
                auto it_cache = kv_cache_versions_.find(event.order_id);
                if (it_cache == kv_cache_versions_.end() || event.version >= it_cache->second) {
                    kv_cache_[event.order_id] = event.payload;
                    kv_cache_versions_[event.order_id] = event.version;
                }

                // Синхронізація з пошуковим індексом (за іменем клієнта)
                auto it = primary_db_.find(event.order_id);
                if (it != primary_db_.end()) {
                    search_index_[it->second.customer].push_back(event.order_id);
                }

                event.processed = true;
            }
        }
    }

    // 3. Запитовий бік (Query Side): Читання з оптимізованого сховища
    std::optional<std::string> get_order_fast(int order_id) const {
        auto it = kv_cache_.find(order_id);
        if (it != kv_cache_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    std::vector<int> search_orders_by_customer(const std::string& customer_name) const {
        auto it = search_index_.find(customer_name);
        if (it != search_index_.end()) {
            return it->second;
        }
        return {};
    }

    // Оновлення статусу замовлення з інкрементом версії
    bool update_order_status(int order_id, const std::string& new_status) {
        auto it = primary_db_.find(order_id);
        if (it == primary_db_.end()) return false;

        it->second.status = new_status;
        it->second.version++;

        std::ostringstream ss;
        ss << "{\"id\":" << order_id << ",\"status\":\"" << new_status << "\"}";

        outbox_.push_back({
            static_cast<int>(outbox_.size() + 1),
            order_id,
            "ORDER_STATUS_UPDATED",
            ss.str(),
            it->second.version,
            false
        });

        return true;
    }

private:
    std::unordered_map<int, Order> primary_db_;
    std::vector<OutboxEvent> outbox_;
    std::unordered_map<int, std::string> kv_cache_;
    std::unordered_map<int, uint64_t> kv_cache_versions_;
    std::unordered_map<std::string, std::vector<int>> search_index_;
};

} // namespace polyglot

int main() {
    using namespace polyglot;
    PolyglotOrderCoordinator coordinator;

    // 1. Створення замовлень
    coordinator.create_order(101, "Alice", 250.0);
    coordinator.create_order(102, "Bob", 120.0);
    coordinator.create_order(103, "Alice", 499.99);

    // До синхронізації кеш порожній
    auto miss = coordinator.get_order_fast(101);
    std::cout << "Cache hit before sync: " << (miss.has_value() ? "YES" : "NO") << std::endl;

    // 2. Фонова обробка Outbox
    coordinator.sync_projections();

    // Після синхронізації дані доступні миттєво
    auto hit = coordinator.get_order_fast(101);
    if (hit) {
        std::cout << "Fast cache result: " << *hit << std::endl;
    }

    // Пошук усіх замовлень клієнта Alice за O(1)
    auto alice_orders = coordinator.search_orders_by_customer("Alice");
    std::cout << "Orders for Alice count: " << alice_orders.size() << std::endl;

    // 3. Оновлення статусу
    coordinator.update_order_status(101, "PAID");
    coordinator.sync_projections();
    std::cout << "Updated cache result: " << *coordinator.get_order_fast(101) << std::endl;

    return 0;
}
