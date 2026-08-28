#include <iostream>
#include <optional>
#include <shared_mutex>
#include <string>
#include <string_view>
#include <unordered_map>

class ThreadSafeRoutingTable {
public:
    ThreadSafeRoutingTable() = default;
    ~ThreadSafeRoutingTable() = default;

    // Заборона копіювання через наявність м'ютекса
    ThreadSafeRoutingTable(const ThreadSafeRoutingTable&) = delete;
    ThreadSafeRoutingTable& operator=(const ThreadSafeRoutingTable&) = delete;

    // Операція читання: безпечний одночасний пошук багатьма потоками
    std::optional<std::string> lookup(std::string_view subnet) const {
        // std::shared_lock захоплює std::shared_mutex у розділюваному режимі (Shared)
        std::shared_lock<std::shared_mutex> lock(rw_mutex_);
        
        auto it = table_.find(std::string(subnet));
        if (it != table_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    // Операція запису: монопольний доступ для додавання або оновлення
    void set_route(std::string subnet, std::string gateway) {
        // std::unique_lock захоплює std::shared_mutex у монопольному режимі (Exclusive)
        std::unique_lock<std::shared_mutex> lock(rw_mutex_);
        table_[std::move(subnet)] = std::move(gateway);
    }

    // Безпечне видалення маршруту
    bool remove_route(std::string_view subnet) {
        std::unique_lock<std::shared_mutex> lock(rw_mutex_);
        return table_.erase(std::string(subnet)) > 0;
    }

    // Отримання поточної кількості записів
    std::size_t size() const {
        std::shared_lock<std::shared_mutex> lock(rw_mutex_);
        return table_.size();
    }

private:
    mutable std::shared_mutex                   rw_mutex_;
    std::unordered_map<std::string, std::string> table_;
};
