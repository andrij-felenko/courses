#include <iostream>
#include <string>
#include <unordered_map>
#include <memory>
#include <future>
#include <mutex>
#include <stdexcept>
#include <chrono>

template <typename T>
class SingleFlight {
public:
    struct Result {
        T value;
        bool shared{false};
        size_t waiters_count{0};
    };

private:
    struct Call {
        std::shared_future<T> future;
        size_t waiters{0};
    };

    std::mutex mu_;
    std::unordered_map<std::string, std::shared_ptr<Call>> table_;

public:
    template <typename Func>
    Result execute(const std::string& key, Func&& fn) {
        std::shared_ptr<Call> call;
        bool is_leader = false;
        std::promise<T> promise;

        {
            std::lock_guard<std::mutex> lock(mu_);
            auto it = table_.find(key);
            if (it != table_.end()) {
                // Вже є активний рейс: стаємо очікувачем
                call = it->second;
                call->waiters++;
            } else {
                // Ми перший запит: стаємо лідером
                call = std::make_shared<Call>();
                call->future = promise.get_future().share();
                table_[key] = call;
                is_leader = true;
            }
        }

        if (is_leader) {
            // Виконання лідерського рейсу з перехопленням винятків
            try {
                T val = fn();
                promise.set_value(val);
            } catch (...) {
                promise.set_exception(std::current_exception());
            }

            // Очищення таблиці після завершення
            std::lock_guard<std::mutex> lock(mu_);
            table_.erase(key);
        }

        // Очікування завершення через shared_future
        T result_value = call->future.get();

        return Result{
            .value = std::move(result_value),
            .shared = !is_leader,
            .waiters_count = call->waiters
        };
    }
};
