#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <shared_mutex>
#include <optional>
#include <chrono>
#include <atomic>
#include <memory>

class TwoTierCoherentCache {
public:
    struct CacheEntry {
        std::string value;
        uint64_t version{0};
        uint64_t lease_token{0};
        std::chrono::steady_clock::time_point expires_at;
        bool is_valid{false};
    };

    explicit TwoTierCoherentCache(std::chrono::seconds default_ttl = std::chrono::seconds(60))
        : default_ttl_(default_ttl), lease_generator_(1) {}

    // 1. Швидке читання з локального L1 кешу (без мережевих затримок)
    [[nodiscard]] std::optional<std::pair<std::string, uint64_t>> 
    get_l1(std::string_view key) const {
        std::shared_lock<std::shared_mutex> lock(mutex_);
        auto it = storage_.find(std::string(key));
        if (it == storage_.end() || !it->second.is_valid) {
            return std::nullopt;
        }

        if (std::chrono::steady_clock::now() >= it->second.expires_at) {
            return std::nullopt; // Термін дії сплив
        }

        return std::make_pair(it->second.value, it->second.version);
    }

    // 2. Видача токена оренди при кеш-промаху (Thundering Herd & Stale-Write Protection)
    [[nodiscard]] uint64_t acquire_lease(std::string_view key) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        uint64_t token = lease_generator_.fetch_add(1, std::memory_order_relaxed);
        
        auto& entry = storage_[std::string(key)];
        entry.lease_token = token;
        entry.is_valid = false;
        return token;
    }

    // 3. Збереження результату читання зі СКБД з перевіркою маркеру оренди
    bool set_with_lease(std::string_view key, std::string_view value, 
                        uint64_t version, uint64_t token) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        auto it = storage_.find(std::string(key));
        
        // Якщо ключ відсутній або оренду було скасовано паралельною інвалідацією — відхиляємо запис
        if (it == storage_.end() || it->second.lease_token != token) {
            return false;
        }

        it->second.value = std::string(value);
        it->second.version = version;
        it->second.expires_at = std::chrono::steady_clock::now() + default_ttl_;
        it->second.is_valid = true;
        it->second.lease_token = 0; // Оренду успішно використано
        return true;
    }

    // 4. Обробник події інвалідації (Redis RESP3 Tracking / Kafka CDC Topic)
    void on_invalidation(std::string_view key, uint64_t mutated_version) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        auto it = storage_.find(std::string(key));
        if (it != storage_.end()) {
            if (it->second.version <= mutated_version) {
                it->second.is_valid = false;
                it->second.lease_token = 0; // Анулювання активної оренди
            }
        }
    }

    // 5. Очищення застарілих елементів
    void purge_expired() {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        const auto now = std::chrono::steady_clock::now();
        for (auto it = storage_.begin(); it != storage_.end(); ) {
            if (!it->second.is_valid || it->second.expires_at <= now) {
                it = storage_.erase(it);
            } else {
                ++it;
            }
        }
    }

private:
    std::chrono::seconds default_ttl_;
    std::atomic<uint64_t> lease_generator_;
    mutable std::shared_mutex mutex_;
    std::unordered_map<std::string, CacheEntry> storage_;
};
