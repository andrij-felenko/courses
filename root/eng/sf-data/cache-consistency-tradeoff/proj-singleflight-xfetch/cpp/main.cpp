// Реалізація Singleflight + XFetch мовою C++ (C++20, RAII, std::shared_mutex)
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <chrono>
#include <random>
#include <cmath>
#include <mutex>
#include <shared_mutex>
#include <condition_variable>
#include <thread>
#include <expected>
#include <vector>

using namespace std::chrono_literals;

class ResilientCache {
public:
    struct CacheEntry {
        std::string value;
        std::chrono::steady_clock::time_point expiry;
        std::chrono::duration<double> compute_time;
        uint64_t lease_token{0};
    };

    explicit ResilientCache(double beta = 1.0) 
        : beta_(beta), rng_(std::random_device{}()) {}

    // Читання або випереджальне оновлення через Singleflight
    std::string get_or_fetch(std::string_view key, 
                             std::chrono::seconds ttl,
                             auto&& db_fetch_fn) {
        // 1. Спроба швидкого паралельного читання (Shared Lock)
        {
            std::shared_lock lock(cache_mutex_);
            auto it = store_.find(std::string(key));
            if (it != store_.end()) {
                if (!should_refresh(it->second)) {
                    return it->second.value; // Швидке влучання
                }
            }
        }

        // 2. Потрібне оновлення: координація через Singleflight
        std::shared_ptr<InFlightCall> call;
        bool is_leader = false;
        {
            std::unique_lock lock(flight_mutex_);
            auto it = in_flight_.find(std::string(key));
            if (it == in_flight_.end()) {
                call = std::make_shared<InFlightCall>();
                in_flight_[std::string(key)] = call;
                is_leader = true;
            } else {
                call = it->second;
            }
        }

        if (!is_leader) {
            // Очікування результату від потоку-лідера
            std::unique_lock lock(call->cv_mutex);
            call->cv.wait(lock, [&] { return call->done; });
            return call->result;
        }

        // 3. Виконання запиту лідером
        const auto t0 = std::chrono::steady_clock::now();
        std::string fresh_val = db_fetch_fn(key);
        const auto t1 = std::chrono::steady_clock::now();
        const std::chrono::duration<double> delta = t1 - t0;

        // 4. Оновлення кешу
        {
            std::unique_lock lock(cache_mutex_);
            auto& entry = store_[std::string(key)];
            entry.value = fresh_val;
            entry.expiry = std::chrono::steady_clock::now() + ttl;
            entry.compute_time = delta;
            entry.lease_token = ++next_lease_;
        }

        // 5. Сповіщення очікувачів та очищення in_flight
        {
            std::unique_lock flight_lock(flight_mutex_);
            {
                std::unique_lock cv_lock(call->cv_mutex);
                call->result = fresh_val;
                call->done = true;
            }
            in_flight_.erase(std::string(key));
        }
        call->cv.notify_all();

        return fresh_val;
    }

    // Інвалідація ключа
    void invalidate(std::string_view key) {
        std::unique_lock lock(cache_mutex_);
        store_.erase(std::string(key));
        ++next_lease_; // Інвалідація активних токенів
    }

private:
    struct InFlightCall {
        std::string result;
        bool done{false};
        std::mutex cv_mutex;
        std::condition_variable cv;
    };

    bool should_refresh(const CacheEntry& entry) {
        const auto now = std::chrono::steady_clock::now();
        if (now >= entry.expiry) return true;

        const auto time_left = std::chrono::duration<double>(entry.expiry - now).count();
        const double delta = entry.compute_time.count();

        std::uniform_real_distribution<double> dist(0.0, 1.0);
        double u = 0.0;
        {
            std::lock_guard lock(rng_mutex_);
            u = dist(rng_);
            if (u <= 0.0) u = 1e-9;
        }

        // Формула XFetch: -beta * delta * ln(u) > time_left
        return (-beta_ * delta * std::log(u)) > time_left;
    }

    double beta_;
    uint64_t next_lease_{1};
    mutable std::shared_mutex cache_mutex_;
    std::unordered_map<std::string, CacheEntry> store_;

    std::mutex flight_mutex_;
    std::unordered_map<std::string, std::shared_ptr<InFlightCall>> in_flight_;

    std::mutex rng_mutex_;
    std::mt19937 rng_;
};
