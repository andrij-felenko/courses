// leader_elector.cpp - Промислова реалізація виборів лідера на C++20
#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <mutex>
#include <atomic>
#include <memory>
#include <functional>
#include <optional>
#include <stop_token>

using namespace std::chrono_literals;

/* --- Імітатор розподіленого координатора консенсусу (etcd / Consul) --- */
class MockCoordinator {
public:
    struct LeaseGrant {
        uint64_t fencing_token;
        bool granted;
    };

    static MockCoordinator& instance() {
        static MockCoordinator inst;
        return inst;
    }

    LeaseGrant try_acquire(std::string_view candidate_id, std::chrono::milliseconds ttl) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto now = std::chrono::steady_clock::now();

        bool can_acquire = false;
        if (!is_allocated_ || now >= expiry_time_) {
            can_acquire = true;
        } else if (current_leader_ == candidate_id) {
            can_acquire = true;
        }

        if (can_acquire) {
            current_leader_ = candidate_id;
            fencing_token_++;
            is_allocated_ = true;
            expiry_time_ = now + ttl;
            return {fencing_token_, true};
        }
        return {0, false};
    }

    bool renew_lease(std::string_view leader_id, uint64_t token, std::chrono::milliseconds ttl) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto now = std::chrono::steady_clock::now();

        if (is_allocated_ && now < expiry_time_ &&
            current_leader_ == leader_id && fencing_token_ == token) {
            expiry_time_ = now + ttl;
            return true;
        }
        return false;
    }

    void resign(std::string_view leader_id, uint64_t token) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (is_allocated_ && current_leader_ == leader_id && fencing_token_ == token) {
            is_allocated_ = false;
            current_leader_.clear();
        }
    }

private:
    std::mutex mutex_;
    std::string current_leader_;
    uint64_t fencing_token_{0};
    std::chrono::steady_clock::time_point expiry_time_;
    bool is_allocated_{false};
};

/* --- Захищене цільове сховище з валідацією фенсингового токена --- */
class ProtectedStorage {
public:
    static ProtectedStorage& instance() {
        static ProtectedStorage inst;
        return inst;
    }

    bool mutate(uint64_t token, int delta, std::string_view caller_id) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (token < last_seen_token_) {
            std::cout << "[" << caller_id << "] ВІДХИЛЕНО: Токен " << token
                      << " застарілий! Чинний токен: " << last_seen_token_ << "\n";
            return false;
        }
        last_seen_token_ = token;
        balance_ += delta;
        std::cout << "[" << caller_id << "] УСПІХ: Мутація з токеном " << token
                  << " зафіксована. Баланс = " << balance_ << "\n";
        return true;
    }

private:
    std::mutex mutex_;
    uint64_t last_seen_token_{0};
    int balance_{1000};
};

/* --- Клієнтський клас управління життєвим циклом лідера --- */
class LeaderElector {
public:
    using PayloadFunc = std::function<void(std::stop_token, uint64_t)>;

    LeaderElector(std::string node_id, std::chrono::milliseconds lease_ttl, PayloadFunc payload)
        : node_id_(std::move(node_id)),
          lease_ttl_(lease_ttl),
          renew_interval_(lease_ttl / 3),
          retry_interval_(lease_ttl / 4),
          payload_func_(std::move(payload)) {
        
        election_thread_ = std::jthread([this](std::stop_token st) {
            run_election_loop(st);
        });
    }

    ~LeaderElector() {
        stop();
    }

    void stop() {
        if (election_thread_.joinable()) {
            election_thread_.request_stop();
            election_thread_.join();
        }
    }

    bool is_leader() const noexcept {
        return is_leading_.load(std::memory_order_relaxed);
    }

private:
    void run_election_loop(std::stop_token st) {
        while (!st.stop_requested()) {
            if (!is_leading_.load(std::memory_order_relaxed)) {
                // Стан STANDBY: намагаємося захопити лізу
                auto grant = MockCoordinator::instance().try_acquire(node_id_, lease_ttl_);
                if (grant.granted) {
                    current_token_ = grant.fencing_token;
                    is_leading_.store(true, std::memory_order_release);
                    std::cout << ">>> [" << node_id_ << "] СТАВ ЛІДЕРОМ! Fencing Token = "
                              << current_token_ << " <<<\n";

                    // Запускаємо корисну роботу лідера у фоновому потоці
                    payload_thread_ = std::jthread([this, token = current_token_](std::stop_token payload_st) {
                        if (payload_func_) {
                            payload_func_(payload_st, token);
                        }
                    });
                } else {
                    std::this_thread::sleep_for(retry_interval_);
                }
            } else {
                // Стан LEADER: оновлюємо лізу
                std::this_thread::sleep_for(renew_interval_);
                if (st.stop_requested()) break;

                bool renewed = MockCoordinator::instance().renew_lease(node_id_, current_token_, lease_ttl_);
                if (!renewed) {
                    std::cout << "!!! [" << node_id_ << "] ВТРАТА ЛІДЕРСТВА: Keep-Alive провалився! !!!\n";
                    is_leading_.store(false, std::memory_order_release);

                    // Зупиняємо бізнес-потік
                    if (payload_thread_.joinable()) {
                        payload_thread_.request_stop();
                        payload_thread_.join();
                    }
                }
            }
        }

        // Акуратне складання повноважень при завершенні роботи
        if (is_leading_.load(std::memory_order_relaxed)) {
            MockCoordinator::instance().resign(node_id_, current_token_);
            is_leading_.store(false, std::memory_order_release);
            if (payload_thread_.joinable()) {
                payload_thread_.request_stop();
                payload_thread_.join();
            }
        }
    }

    std::string node_id_;
    std::chrono::milliseconds lease_ttl_;
    std::chrono::milliseconds renew_interval_;
    std::chrono::milliseconds retry_interval_;
    PayloadFunc payload_func_;

    std::atomic<bool> is_leading_{false};
    uint64_t current_token_{0};

    std::jthread election_thread_;
    std::jthread payload_thread_;
};

/* --- Точка входу: демонстрація відмови та захисту токенами --- */
int main() {
    std::cout << "=== Запуск кластера виборів лідера (C++20) ===\n";

    auto business_logic = [](std::stop_token st, uint64_t token) {
        while (!st.stop_requested()) {
            ProtectedStorage::instance().mutate(token, 100, "АктивнийЛідер");
            std::this_thread::sleep_for(600ms);
        }
    };

    LeaderElector node_1("Вузол-1", 1200ms, business_logic);
    std::this_thread::sleep_for(200ms);
    LeaderElector node_2("Вузол-2", 1200ms, business_logic);

    // Вузол-1 захоплює лідерство і працює 2 секунди
    std::this_thread::sleep_for(2s);

    std::cout << "\n--- Імітація аварійного відключення Вузла-1 ---\n";
    node_1.stop(); // Вузол-1 зупиняється без поновлення лізи

    // Вузол-2 виявляє прострочення лізи та стає новим лідером
    std::this_thread::sleep_for(3s);

    std::cout << "=== Завершення роботи кластера ===\n";
    return 0;
}
