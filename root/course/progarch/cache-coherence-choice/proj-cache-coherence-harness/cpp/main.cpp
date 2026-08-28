#include <iostream>
#include <string>
#include <unordered_map>
#include <mutex>
#include <optional>
#include <memory>
#include <vector>

struct UserRecord {
    std::string id;
    std::string address;
    uint64_t version{0};
};

class DistributedCache {
private:
    struct CacheEntry {
        std::string value;
        uint64_t version;
    };
    std::unordered_map<std::string, CacheEntry> entries_;
    mutable std::mutex mutex_;

public:
    std::optional<CacheEntry> get(const std::string& key) const {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = entries_.find(key);
        if (it != entries_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    bool put_if_newer(const std::string& key, const std::string& value, uint64_t version) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = entries_.find(key);
        if (it != entries_.end()) {
            if (it->second.version >= version) {
                std::cout << "[CPP Cache Guard] Stale write rejected for key: " << key
                          << " (Current ver: " << it->second.version
                          << " >= Incoming ver: " << version << ")\n";
                return false;
            }
        }
        entries_[key] = CacheEntry{value, version};
        std::cout << "[CPP Cache] Key '" << key << "' updated to version " << version << "\n";
        return true;
    }

    void evict(const std::string& key) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (entries_.erase(key) > 0) {
            std::cout << "[CPP Cache Evict] Key '" << key << "' evicted successfully.\n";
        }
    }
};

class PrimaryDatabase {
private:
    std::unordered_map<std::string, UserRecord> records_;
    mutable std::mutex mutex_;

public:
    PrimaryDatabase() {
        records_["user_100"] = {"user_100", "Initial Central St", 1};
    }

    std::optional<UserRecord> read(const std::string& id) const {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = records_.find(id);
        if (it != records_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    UserRecord update_address(const std::string& id, const std::string& new_addr) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto& rec = records_[id];
        rec.address = new_addr;
        rec.version++;
        return rec;
    }
};

// Демонстрація контролера сервісу з інвалідацією
class UserService {
private:
    PrimaryDatabase db_;
    std::shared_ptr<DistributedCache> cache_;

public:
    explicit UserService(std::shared_ptr<DistributedCache> cache)
        : cache_(std::move(cache)) {}

    // Безаварійне оновлення з патерном Eviction
    void update_user_address(const std::string& id, const std::string& new_address) {
        // 1. Атомарне оновлення у первинній БД
        UserRecord updated = db_.update_address(id, new_address);

        // 2. БЕЗПЕЧНА ІНВАЛІДАЦІЯ: Видаляємо ключ замість перезапису тіла
        cache_->evict(id);
    }

    std::string get_user_address(const std::string& id) {
        // 1. Спроба зчитати з кешу
        auto cached = cache_->get(id);
        if (cached) {
            return cached->value;
        }

        // 2. Cache Miss -> Зчитуємо з первинної БД
        auto db_rec = db_.read(id);
        if (!db_rec) return "";

        // 3. Записуємо в кеш лише якщо версія актуальна
        cache_->put_if_newer(id, db_rec->address, db_rec->version);
        return db_rec->address;
    }
};

int main() {
    auto cache = std::make_shared<DistributedCache>();
    UserService service(cache);

    std::cout << "--- C++ Read / Miss / Evict Pipeline ---\n";
    std::cout << "First Read (Miss): " << service.get_user_address("user_100") << "\n";
    std::cout << "Second Read (Hit): " << service.get_user_address("user_100") << "\n";

    service.update_user_address("user_100", "Updated North Ave");
    std::cout << "Read After Eviction (Miss & Refresh): " << service.get_user_address("user_100") << "\n";

    return 0;
}
