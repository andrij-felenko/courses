#include <iostream>
#include <string>
#include <unordered_map>
#include <memory>
#include <mutex>
#include <future>
#include <chrono>
#include <random>
#include <cmath>
#include <functional>
#include <thread>
#include <vector>

// Запис кешу з підтримкою метаданих XFetch
template <typename T>
struct CacheEntry {
    T value;
    std::chrono::steady_clock::time_point expiry;
    std::chrono::duration<double> computation_delta; // δ у секундах
};

// Рушій захисту від навали на кеш
template <typename T>
class StampedeGuard {
public:
    using FetcherFunc = std::function<T()>;

    StampedeGuard(double beta = 1.0) : beta_(beta), rng_(std::random_device{}()) {}

    // Отримання значення з гарантованим захистом від лавини запитів
    T get_or_compute(const std::string& key, std::chrono::seconds ttl, FetcherFunc fetcher) {
        // 1. Швидка перевірка наявності в локальному сховищі
        {
            std::lock_guard<std::mutex> lock(cache_mutex_);
            auto it = cache_.find(key);
            if (it != cache_.end()) {
                const auto& entry = it->second;
                if (!should_recompute_xfetch(entry)) {
                    return entry.value; // Кеш свіжий або XFetch вирішив не оновлювати зараз
                }
            }
        }

        // 2. Якщо потрібен перерахунок — задіюємо Single-Flight дедуплікацію
        std::shared_future<T> active_future;
        bool is_leader = false;

        {
            std::lock_guard<std::mutex> lock(flights_mutex_);
            auto it = in_flight_.find(key);
            if (it != in_flight_.end()) {
                // Вже є активний рейс: стаємо підписником
                active_future = it->second;
            } else {
                // Ми — лідер рейсу: створюємо обіцянку
                is_leader = true;
                auto promise = std::make_shared<std::promise<T>>();
                active_future = promise->get_future().share();
                in_flight_[key] = active_future;

                // Запускаємо асинхронне виконання в окремому потоці/пулі
                std::thread([this, key, ttl, fetcher, promise]() {
                    auto start = std::chrono::steady_clock::now();
                    try {
                        T result = fetcher();
                        auto delta = std::chrono::steady_clock::now() - start;

                        // Оновлюємо кеш під м'ютексом
                        {
                            std::lock_guard<std::mutex> c_lock(cache_mutex_);
                            cache_[key] = CacheEntry<T>{
                                result,
                                std::chrono::steady_clock::now() + ttl,
                                std::chrono::duration<double>(delta)
                            };
                        }

                        promise->set_value(result);
                    } catch (...) {
                        promise->set_exception(std::current_exception());
                    }

                    // Очищаємо запис про рейс
                    {
                        std::lock_guard<std::mutex> f_lock(flights_mutex_);
                        in_flight_.erase(key);
                    }
                }).detach();
            }
        }

        // 3. Усі потоки (і лідер, і підписники) чекають на єдиний результат
        return active_future.get();
    }

private:
    // Оцінка за формулою XFetch: now - delta * beta * ln(U) > expiry
    bool should_recompute_xfetch(const CacheEntry<T>& entry) {
        auto now = std::chrono::steady_clock::now();
        if (now >= entry.expiry) {
            return true; // Термін дії повністю вичерпано
        }

        if (entry.computation_delta.count() <= 0.0) {
            return false;
        }

        std::uniform_real_distribution<double> dist(0.0001, 1.0);
        double u = dist(rng_);
        double early_shift_sec = -entry.computation_delta.count() * beta_ * std::log(u);
        auto threshold = now + std::chrono::duration<double>(early_shift_sec);

        return threshold > entry.expiry;
    }

    double beta_;
    std::mt19937 rng_;
    std::mutex cache_mutex_;
    std::unordered_map<std::string, CacheEntry<T>> cache_;
    std::mutex flights_mutex_;
    std::unordered_map<std::string, std::shared_future<T>> in_flight_;
};
