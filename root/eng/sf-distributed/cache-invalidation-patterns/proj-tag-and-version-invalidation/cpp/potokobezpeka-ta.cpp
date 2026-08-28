#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <memory>
#include <chrono>
#include <mutex>
#include <optional>
#include <thread>
#include <functional>

struct CacheEntry {
    std::string value;
    std::chrono::steady_clock::time_point expires_at;
    uint64_t lease_token{0};
    std::vector<std::string> tags;
};

class InvalidationEngine {
public:
    // Запис значення з прив'язкою до списку тегів
    void set(std::string_view key, std::string_view value,
             std::chrono::seconds ttl, const std::vector<std::string>& tags = {}) {
        std::unique_lock<std::mutex> lock(mutex_);
        std::string k(key);
        
        CacheEntry entry;
        entry.value = std::string(value);
        entry.expires_at = std::chrono::steady_clock::now() + ttl;
        entry.lease_token = ++next_lease_id_;
        entry.tags = tags;

        // Оновлюємо інвертований індекс тегів
        for (const auto& tag : tags) {
            tag_to_keys_[tag].insert(k);
        }

        cache_[k] = std::move(entry);
    }

    // Читання значення з перевіркою TTL
    std::optional<std::string> get(std::string_view key) {
        std::unique_lock<std::mutex> lock(mutex_);
        auto it = cache_.find(std::string(key));
        if (it == cache_.end()) {
            return std::nullopt;
        }

        if (std::chrono::steady_clock::now() > it->second.expires_at) {
            erase_internal(it->first);
            return std::nullopt;
        }

        return it->second.value;
    }

    // Пряме видалення одного ключа
    bool del(std::string_view key) {
        std::unique_lock<std::mutex> lock(mutex_);
        return erase_internal(std::string(key));
    }

    // Інвалідація всіх ключів за заданим тегом
    size_t purge_tag(std::string_view tag) {
        std::unique_lock<std::mutex> lock(mutex_);
        auto it = tag_to_keys_.find(std::string(tag));
        if (it == tag_to_keys_.end()) {
            return 0;
        }

        std::unordered_set<std::string> keys_to_remove = std::move(it->second);
        tag_to_keys_.erase(it);

        size_t purged_count = 0;
        for (const auto& key : keys_to_remove) {
            if (cache_.erase(key) > 0) {
                purged_count++;
            }
        }
        return purged_count;
    }

    // Отримання поточної епохи простору імен
    uint64_t get_generation(std::string_view ns) {
        std::unique_lock<std::mutex> lock(mutex_);
        auto it = namespace_epochs_.find(std::string(ns));
        if (it == namespace_epochs_.end()) {
            namespace_epochs_[std::string(ns)] = 1;
            return 1;
        }
        return it->second;
    }

    // Інкремент епохи (O(1) інвалідація простору імен)
    uint64_t bump_generation(std::string_view ns) {
        std::unique_lock<std::mutex> lock(mutex_);
        return ++namespace_epochs_[std::string(ns)];
    }

    // Формування версійного ключа з поточною епохою
    std::string make_versioned_key(std::string_view ns, std::string_view raw_key) {
        uint64_t gen = get_generation(ns);
        return std::string(ns) + ":v" + std::to_string(gen) + ":" + std::string(raw_key);
    }

    // Відкладене подвійне видалення (Delayed Double-Delete)
    void delayed_double_delete(std::string key, std::chrono::milliseconds delay) {
        // Перше негайне видалення
        del(key);

        // Друге відкладене видалення у фоновому потоці після затримки реплікації
        std::thread([this, key = std::move(key), delay]() {
            std::this_thread::sleep_for(delay);
            this->del(key);
        }).detach();
    }

private:
    bool erase_internal(const std::string& key) {
        auto it = cache_.find(key);
        if (it == cache_.end()) {
            return false;
        }

        // Очищаємо зворотні посилання в індексі тегів
        for (const auto& tag : it->second.tags) {
            auto tag_it = tag_to_keys_.find(tag);
            if (tag_it != tag_to_keys_.end()) {
                tag_it->second.erase(key);
                if (tag_it->second.empty()) {
                    tag_to_keys_.erase(tag_it);
                }
            }
        }

        cache_.erase(it);
        return true;
    }

    std::mutex mutex_;
    std::unordered_map<std::string, CacheEntry> cache_;
    std::unordered_map<std::string, std::unordered_set<std::string>> tag_to_keys_;
    std::unordered_map<std::string, uint64_t> namespace_epochs_;
    uint64_t next_lease_id_{1000};
};
