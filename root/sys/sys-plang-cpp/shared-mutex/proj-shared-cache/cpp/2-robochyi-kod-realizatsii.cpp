#include <iostream>
#include <string>
#include <unordered_map>
#include <shared_mutex>
#include <optional>
#include <chrono>
#include <vector>
#include <thread>

template <typename Key, typename Value>
class ThreadSafeCache {
public:
    using Clock = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;

    struct CacheEntry {
        Value value;
        TimePoint expiry;
    };

    explicit ThreadSafeCache(std::chrono::milliseconds default_ttl)
        : default_ttl_(default_ttl) {}

    // Читання запису з кешу (Shared Mode)
    std::optional<Value> get(const Key& key) const {
        std::shared_lock<std::shared_mutex> lock(mutex_);

        auto it = cache_.find(key);
        if (it == cache_.end()) {
            return std::nullopt;
        }

        // Перевірка часу життя (TTL)
        if (Clock::now() > it->second.expiry) {
            return std::nullopt; // Запис застарів, але вилучиться пізніше
        }

        return it->second.value;
    }

    // Запис або оновлення елемента (Exclusive Mode)
    void put(const Key& key, Value value, std::optional<std::chrono::milliseconds> ttl = std::nullopt) {
        auto duration = ttl.value_or(default_ttl_);
        TimePoint expiry = Clock::now() + duration;

        std::unique_lock<std::shared_mutex> lock(mutex_);
        cache_[key] = CacheEntry{std::move(value), expiry};
    }

    // Примусове вилучення запису (Exclusive Mode)
    bool remove(const Key& key) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        return cache_.erase(key) > 0;
    }

    // Фонове вичищення застарілих записів (Exclusive Mode)
    size_t purge_expired() {
        std::vector<Key> expired_keys;
        auto now = Clock::now();

        // Фаза 1: Пошук застарілих ключів у сумісному режимі для мінімізації блокування
        {
            std::shared_lock<std::shared_mutex> lock(mutex_);
            for (const auto& [key, entry] : cache_) {
                if (now > entry.expiry) {
                    expired_keys.push_back(key);
                }
            }
        }

        if (expired_keys.empty()) {
            return 0;
        }

        // Фаза 2: Монопольне вилучення знайдених ключів
        std::unique_lock<std::shared_mutex> lock(mutex_);
        size_t purged_count = 0;
        for (const auto& key : expired_keys) {
            auto it = cache_.find(key);
            if (it != cache_.end() && now > it->second.expiry) {
                cache_.erase(it);
                ++purged_count;
            }
        }
        return purged_count;
    }

    // Отримання поточної кількості елементів
    size_t size() const {
        std::shared_lock<std::shared_mutex> lock(mutex_);
        return cache_.size();
    }

private:
    mutable std::shared_mutex mutex_;
    std::unordered_map<Key, CacheEntry> cache_;
    std::chrono::milliseconds default_ttl_;
};

int main() {
    ThreadSafeCache<std::string, std::string> dns_cache(std::chrono::seconds(2));

    dns_cache.put("example.com", "93.184.216.34");
    dns_cache.put("local.dev", "127.0.0.1", std::chrono::milliseconds(500));

    // Паралельні потоки читання
    auto reader = [&dns_cache](int id) {
        for (int i = 0; i < 5; ++i) {
            auto val = dns_cache.get("example.com");
            if (val) {
                std::cout << "[Reader " << id << "] Found: " << *val << "\n";
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    };

    std::thread t1(reader, 1);
    std::thread t2(reader, 2);

    t1.join();
    t2.join();

    std::cout << "Purged expired entries: " << dns_cache.purge_expired() << "\n";
    return 0;
}
