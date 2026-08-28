#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <thread>
#include <expected>
#include <vector>

class EdgeCacheProxy {
public:
    struct CacheEntry {
        std::string data;
        std::chrono::steady_clock::time_point expires_at;
    };

    struct InflightState {
        bool is_done{false};
        std::string error_message;
        std::condition_variable cv;
    };

    explicit EdgeCacheProxy(std::chrono::seconds default_ttl) 
        : default_ttl_(default_ttl) {}

    // Отримання ресурсу з кешу або через єдиний запит до Origin
    std::expected<std::string, std::string> get(std::string_view key) {
        std::string key_str(key);
        std::unique_lock<std::mutex> lock(mutex_);

        auto now = std::chrono::steady_clock::now();

        // 1. Перевірка валідного запису в кеші
        auto cache_it = cache_.find(key_str);
        if (cache_it != cache_.end() && cache_it->second.expires_at > now) {
            return cache_it->second.data; // Cache HIT
        }

        // 2. Перевірка, чи запит уже виконується іншим потоком
        auto inflight_it = inflight_.find(key_str);
        if (inflight_it != inflight_.end()) {
            auto state = inflight_it->second;
            // Очікуємо завершення запиту першим потоком
            state->cv.wait(lock, [&state]() { return state->is_done; });

            if (!state->error_message.empty()) {
                return std::unexpected(state->error_message);
            }

            auto updated_cache_it = cache_.find(key_str);
            if (updated_cache_it != cache_.end()) {
                return updated_cache_it->second.data;
            }
            return std::unexpected("Запис відсутній після розблокування");
        }

        // 3. Ми — перший потік: реєструємо об'єкт InflightState
        auto state = std::make_shared<InflightState>();
        inflight_[key_str] = state;

        // Звільняємо м'ютекс на час звернення до мережі
        lock.unlock();

        auto origin_result = fetch_from_origin(key_str);

        // 4. Повертаємо блокування та оновлюємо стан для всіх очікуючих
        lock.lock();

        if (origin_result.has_value()) {
            cache_[key_str] = CacheEntry{
                .data = origin_result.value(),
                .expires_at = std::chrono::steady_clock::now() + default_ttl_
            };
        } else {
            state->error_message = origin_result.error();
        }

        state->is_done = true;
        inflight_.erase(key_str);

        // Сповіщаємо всі очікуючі потоки
        state->cv.notify_all();

        return origin_result;
    }

private:
    std::chrono::seconds default_ttl_;
    std::mutex mutex_;
    std::unordered_map<std::string, CacheEntry> cache_;
    std::unordered_map<std::string, std::shared_ptr<InflightState>> inflight_;

    // Симуляція запиту до Origin (затримка 100 мс)
    static std::expected<std::string, std::string> fetch_from_origin(const std::string& key) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        return "Вміст для ресурсу [" + key + "] з джерела Origin";
    }
};
