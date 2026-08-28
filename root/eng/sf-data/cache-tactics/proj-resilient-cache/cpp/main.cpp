#include <iostream>
#include <string>
#include <unordered_map>
#include <shared_mutex>
#include <mutex>
#include <chrono>
#include <random>
#include <optional>
#include <functional>
#include <thread>
#include <memory>

template <typename T>
class ResilientCache {
public:
    struct Entry {
        std::optional<T> value;    // std::nullopt означає Negative Cache (404)
        std::chrono::steady_clock::time_point soft_expiry;
        std::chrono::steady_clock::time_point hard_expiry;
        bool is_refreshing{false};
    };

    struct Options {
        std::chrono::seconds default_ttl{3600};
        std::chrono::seconds negative_ttl{60};
        double soft_ratio{0.75};
        double jitter_ratio{0.15};
    };

    explicit ResilientCache(Options opts = Options{}) : opts_(opts) {}

    // Отримання значення з автоматичним застосуванням Stale-While-Revalidate
    std::optional<T> get_or_load(const std::string& key,
                                 std::function<std::optional<T>()> loader) {
        const auto now = std::chrono::steady_clock::now();

        // 1. Спроба швидкого паралельного читання (Shared Lock)
        {
            std::shared_lock<std::shared_mutex> lock(rw_mutex_);
            auto it = store_.find(key);
            if (it != store_.end() && now < it->second.hard_expiry) {
                // Перевірка необхідності фонового оновлення (Soft TTL)
                if (now >= it->second.soft_expiry && !it->second.is_refreshing) {
                    lock.unlock();
                    try_spawn_async_refresh(key, loader);
                    // Повертаємо поточне значення з кешу (Stale Hit)
                    std::shared_lock<std::shared_mutex> relock(rw_mutex_);
                    auto it_stale = store_.find(key);
                    return (it_stale != store_.end()) ? it_stale->second.value : std::nullopt;
                }
                return it->second.value; // Свіже влучання (Fresh Hit або Negative Hit)
            }
        }

        // 2. Синхронний промах (Hard Miss): блокуючий виклик до бази даних
        return load_and_store_sync(key, loader);
    }

    // Примусова інвалідація ключа при оновленні сутності
    void invalidate(const std::string& key) {
        std::unique_lock<std::shared_mutex> lock(rw_mutex_);
        store_.erase(key);
    }

private:
    std::chrono::seconds compute_jittered_ttl(std::chrono::seconds base) {
        static thread_local std::mt19937 gen(std::random_device{}());
        std::uniform_real_distribution<double> dist(-opts_.jitter_ratio, opts_.jitter_ratio);
        double factor = 1.0 + dist(gen);
        return std::chrono::duration_cast<std::chrono::seconds>(base * factor);
    }

    void try_spawn_async_refresh(const std::string& key,
                                 std::function<std::optional<T>()> loader) {
        std::unique_lock<std::shared_mutex> lock(rw_mutex_);
        auto it = store_.find(key);
        if (it == store_.end() || it->second.is_refreshing) {
            return; // Рейс уже виконується іншим потоком (Single-Flight)
        }
        it->second.is_refreshing = true;

        // Запуск асинхронного фонового оновлення
        std::thread([this, key, loader]() {
            try {
                auto fresh = loader();
                store_value(key, fresh);
            } catch (...) {
                // У разі помилки джерела скидаємо прапорець, залишаючи Stale дані
                std::unique_lock<std::shared_mutex> err_lock(rw_mutex_);
                auto it_err = store_.find(key);
                if (it_err != store_.end()) {
                    it_err->second.is_refreshing = false;
                    // Подовжуємо Soft TTL на 30 секунд для повторної спроби
                    it_err->second.soft_expiry = std::chrono::steady_clock::now() + std::chrono::seconds(30);
                }
            }
        }).detach();
    }

    std::optional<T> load_and_store_sync(const std::string& key,
                                         std::function<std::optional<T>()> loader) {
        auto val = loader();
        store_value(key, val);
        return val;
    }

    void store_value(const std::string& key, const std::optional<T>& val) {
        const auto now = std::chrono::steady_clock::now();
        const bool is_negative = !val.has_value();
        const auto base_ttl = is_negative ? opts_.negative_ttl : opts_.default_ttl;
        const auto actual_ttl = compute_jittered_ttl(base_ttl);

        Entry entry;
        entry.value = val;
        entry.soft_expiry = now + std::chrono::duration_cast<std::chrono::milliseconds>(actual_ttl * opts_.soft_ratio);
        entry.hard_expiry = now + actual_ttl;
        entry.is_refreshing = false;

        std::unique_lock<std::shared_mutex> lock(rw_mutex_);
        store_[key] = std::move(entry);
    }

    Options opts_;
    std::unordered_map<std::string, Entry> store_;
    mutable std::shared_mutex rw_mutex_;
};
