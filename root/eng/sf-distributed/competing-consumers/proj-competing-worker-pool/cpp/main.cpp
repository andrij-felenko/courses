#include <iostream>
#include <vector>
#include <string>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <optional>
#include <memory>
#include <atomic>
#include <stop_token>

using namespace std::chrono_literals;

enum class MessageState {
    Available,
    InFlight,
    Completed,
    Dead
};

struct Message {
    int id;
    std::string payload;
    std::chrono::seconds workDuration;
    bool shouldFail;
    int deliveryCount{0};
    std::chrono::steady_clock::time_point leaseExpiry;
    MessageState state{MessageState::Available};
};

class CompetingQueueBroker {
public:
    explicit CompetingQueueBroker(int maxCapacity = 64, int maxAttempts = 3)
        : maxCapacity_(maxCapacity), maxDeliveryAttempts_(maxAttempts) {}

    bool publish(int id, std::string payload, std::chrono::seconds duration, bool shouldFail) {
        std::unique_lock<std::mutex> lock(mutex_);
        if (messages_.size() >= maxCapacity_) {
            return false;
        }

        messages_.push_back(std::make_unique<Message>(Message{
            id,
            std::move(payload),
            duration,
            shouldFail,
            0,
            std::chrono::steady_clock::time_point{},
            MessageState::Available
        }));

        cv_.notify_one();
        return true;
    }

    // Оренда задачі воркером з контролем таймауту видимості
    std::unique_ptr<Message>* acquireLease(std::chrono::seconds visibilityTimeout, std::stop_token stopToken) {
        std::unique_lock<std::mutex> lock(mutex_);

        while (!stopToken.stop_requested() && !isShutdown_) {
            auto now = std::chrono::steady_clock::now();
            std::unique_ptr<Message>* candidate = nullptr;

            for (auto& msg : messages_) {
                if (msg->state == MessageState::Available) {
                    candidate = &msg;
                    break;
                }
                if (msg->state == MessageState::InFlight && msg->leaseExpiry <= now) {
                    std::cout << "[Broker] Таймаут оренди для M#" << msg->id << " минув! Повторна видача.\n";
                    candidate = &msg;
                    break;
                }
            }

            if (candidate) {
                auto& msg = *candidate;
                msg->deliveryCount++;
                if (msg->deliveryCount > maxDeliveryAttempts_) {
                    std::cout << "[Broker → DLQ] M#" << msg->id 
                              << " перевищив ліміт спроб -> Переміщено в мертву чергу!\n";
                    msg->state = MessageState::Dead;
                    continue;
                }

                msg->state = MessageState::InFlight;
                msg->leaseExpiry = now + visibilityTimeout;
                return candidate;
            }

            cv_.wait_for(lock, 500ms);
        }

        return nullptr;
    }

    void renewLease(int msgId, std::chrono::seconds additionalTime) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto now = std::chrono::steady_clock::now();
        for (auto& msg : messages_) {
            if (msg->id == msgId && msg->state == MessageState::InFlight) {
                msg->leaseExpiry = now + additionalTime;
                return;
            }
        }
    }

    void acknowledge(int msgId) {
        std::lock_guard<std::mutex> lock(mutex_);
        for (auto& msg : messages_) {
            if (msg->id == msgId && msg->state == MessageState::InFlight) {
                msg->state = MessageState::Completed;
                std::cout << "[Broker] ACK підтверджено для M#" << msgId << " (Виконано).\n";
                return;
            }
        }
    }

    void reject(int msgId) {
        std::lock_guard<std::mutex> lock(mutex_);
        for (auto& msg : messages_) {
            if (msg->id == msgId && msg->state == MessageState::InFlight) {
                msg->state = MessageState::Available;
                msg->leaseExpiry = {};
                std::cout << "[Broker] NACK для M#" << msgId << " -> Повернуто в чергу.\n";
                cv_.notify_one();
                return;
            }
        }
    }

    void shutdown() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            isShutdown_ = true;
        }
        cv_.notify_all();
    }

private:
    const size_t maxCapacity_;
    const int maxDeliveryAttempts_;
    std::vector<std::unique_ptr<Message>> messages_;
    std::mutex mutex_;
    std::condition_variable cv_;
    bool isShutdown_{false};
};

// RAII обгортка для подовження лізи (Heartbeat)
class LeaseHeartbeat {
public:
    LeaseHeartbeat(CompetingQueueBroker& broker, int msgId, std::chrono::seconds interval, std::chrono::seconds leaseDuration)
        : broker_(broker), msgId_(msgId), interval_(interval), leaseDuration_(leaseDuration), running_(true) {
        worker_ = std::jthread([this](std::stop_token st) {
            while (!st.stop_requested() && running_) {
                std::this_thread::sleep_for(interval_);
                if (!running_) break;
                broker_.renewLease(msgId_, leaseDuration_);
                std::cout << "[Heartbeat] ⟳ Поновлено оренду для M#" << msgId_ << "\n";
            }
        });
    }

    ~LeaseHeartbeat() {
        stop();
    }

    void stop() {
        running_ = false;
        if (worker_.joinable()) {
            worker_.request_stop();
        }
    }

private:
    CompetingQueueBroker& broker_;
    int msgId_;
    std::chrono::seconds interval_;
    std::chrono::seconds leaseDuration_;
    std::atomic<bool> running_{false};
    std::jthread worker_;
};

void runWorker(int workerId, CompetingQueueBroker& broker, std::stop_token stopToken) {
    std::cout << "[Worker-" << workerId << "] Запущено.\n";
    constexpr auto visibilityTimeout = 2s;

    while (!stopToken.stop_requested()) {
        auto* msgPtr = broker.acquireLease(visibilityTimeout, stopToken);
        if (!msgPtr || stopToken.stop_requested()) {
            break;
        }

        const auto& msg = **msgPtr;
        const int msgId = msg.id;
        const auto duration = msg.workDuration;
        const bool shouldFail = msg.shouldFail;

        std::cout << "[Worker-" << workerId << "] Взяв M#" << msgId 
                  << " («" << msg.payload << "»), час: " << duration.count() 
                  << "с (спроба " << msg.deliveryCount << ")\n";

        // Якщо робота перевищує половину таймауту видимості, вмикаємо фоновий Heartbeat
        std::optional<LeaseHeartbeat> heartbeat;
        if (duration >= visibilityTimeout) {
            heartbeat.emplace(broker, msgId, 1s, visibilityTimeout);
        }

        bool success = true;
        if (shouldFail) {
            std::this_thread::sleep_for(500ms);
            std::cout << "[Worker-" << workerId << "] ✖ Помилка обробки M#" << msgId << "!\n";
            heartbeat.reset();
            broker.reject(msgId);
            success = false;
        } else {
            std::this_thread::sleep_for(duration);
        }

        if (success) {
            heartbeat.reset();
            broker.acknowledge(msgId);
            std::cout << "[Worker-" << workerId << "] ✔ Успішно завершив M#" << msgId << "\n";
        }
    }

    std::cout << "[Worker-" << workerId << "] Зупинився.\n";
}

int main() {
    CompetingQueueBroker broker;
    std::vector<std::jthread> workers;

    for (int i = 1; i <= 4; ++i) {
        workers.emplace_back([i, &broker](std::stop_token st) {
            runWorker(i, broker, st);
        });
    }

    broker.publish(201, "Швидка задача (1с)", 1s, false);
    broker.publish(202, "Важка задача (4с + Heartbeat)", 4s, false);
    broker.publish(203, "Отруйна задача (викличе NACK)", 1s, true);
    broker.publish(204, "Паралельна задача (2с)", 2s, false);

    std::this_thread::sleep_for(7s);

    broker.shutdown();
    for (auto& w : workers) {
        w.request_stop();
    }

    std::cout << "Всі ресурси пулу успішно вивільнено.\n";
    return 0;
}
