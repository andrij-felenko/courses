#include <iostream>
#include <string>
#include <vector>
#include <queue>
#include <memory>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <unordered_set>
#include <unordered_map>
#include <chrono>
#include <functional>
#include <atomic>
#include <optional>
#include <sstream>

// ── 1. СТРУКТУРИ ДАНИХ ТА КОНВЕРТ ПОВІДОМЛЕННЯ ──────────────────────────────
struct MessageHeaders {
    std::string id;                         // Унікальний UUIDv7
    std::string partition_key;              // Ключ для збереження порядку (наприклад, account_id)
    std::string destination;                // Назва черги
    int64_t timestamp_ms = 0;
    uint32_t delivery_attempt = 1;
};

template <typename T>
struct Message {
    MessageHeaders headers;
    T payload;
};

// Бізнес-подія замовлення
struct PaymentEvent {
    std::string order_id;
    std::string account_id;
    uint64_t amount_cents;
    std::string action; // "CREATE", "DEPOSIT", "WITHDRAW"
};

// ── 2. ДЕСКРИПТОР РУЧНОГО ПІДТВЕРДЖЕННЯ (ACKNOWLEDGMENT HANDLE) ────────────
enum class AckStatus { UNPROCESSED, ACKED, NACKED, DLQ_ROUTED };

class AcknowledgmentHandle {
private:
    std::string message_id_;
    AckStatus status_ = AckStatus::UNPROCESSED;
    std::function<void(const std::string&, AckStatus, const std::string&)> callback_;

public:
    AcknowledgmentHandle(std::string message_id,
                         std::function<void(const std::string&, AckStatus, const std::string&)> cb)
        : message_id_(std::move(message_id)), callback_(std::move(cb)) {}

    ~AcknowledgmentHandle() {
        if (status_ == AckStatus::UNPROCESSED && callback_) {
            // RAII-захист: якщо воркер впав або не викликав жодного методу — повертаємо в чергу
            callback_(message_id_, AckStatus::NACKED, "Worker exception / unhandled exit");
        }
    }

    void ack() {
        if (status_ != AckStatus::UNPROCESSED) return;
        status_ = AckStatus::ACKED;
        callback_(message_id_, AckStatus::ACKED, "");
    }

    void nack(const std::string& reason) {
        if (status_ != AckStatus::UNPROCESSED) return;
        status_ = AckStatus::NACKED;
        callback_(message_id_, AckStatus::NACKED, reason);
    }

    void rejectToDlq(const std::string& reason) {
        if (status_ != AckStatus::UNPROCESSED) return;
        status_ = AckStatus::DLQ_ROUTED;
        callback_(message_id_, AckStatus::DLQ_ROUTED, reason);
    }
};

// ── 3. ВХІДНЕ СХОВИЩЕ ІДЕМПОТЕНТНОСТІ (INBOX REPOSITORY) ───────────────────
class ThreadSafeInbox {
private:
    std::mutex mutex_;
    std::unordered_set<std::string> processed_ids_;

public:
    // Повертає true, якщо повідомлення нове, або false, якщо це дублікат
    bool tryClaim(const std::string& message_id) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (processed_ids_.contains(message_id)) {
            return false; // Дубль знайдено!
        }
        processed_ids_.insert(message_id);
        return true;
    }
};

// ── 4. ДОМЕННИЙ СЕРВІС (BUSINESS SERVICE) ──────────────────────────────────
class BankingDomainService {
private:
    std::unordered_map<std::string, int64_t> account_balances_;
    std::mutex service_mutex_;

public:
    void processPayment(const PaymentEvent& event) {
        std::lock_guard<std::mutex> lock(service_mutex_);
        
        // Симуляція перевірки отруйного повідомлення (Poison Pill)
        if (event.amount_cents == 0 && event.action != "CREATE") {
            throw std::invalid_argument("Poison Pill: Zero payment amount is invalid!");
        }

        if (event.action == "CREATE") {
            account_balances_[event.account_id] = 0;
            std::cout << "  [Domain] Створено рахунок " << event.account_id << "\n";
        } else if (event.action == "DEPOSIT") {
            account_balances_[event.account_id] += event.amount_cents;
            std::cout << "  [Domain] Рахунок " << event.account_id << " поповнено на " 
                      << event.amount_cents << " коп. Баланс: " << account_balances_[event.account_id] << "\n";
        } else if (event.action == "WITHDRAW") {
            account_balances_[event.account_id] -= event.amount_cents;
            std::cout << "  [Domain] З рахунку " << event.account_id << " списано " 
                      << event.amount_cents << " коп. Баланс: " << account_balances_[event.account_id] << "\n";
        }
    }
};

// ── 5. ШАРДОВАНИЙ ДИСПЕТЧЕР З PARTITION AFFINITY ТА ПУЛОМ ВОРКЕРІВ ──────────
class KeyPartitionedDispatcher {
private:
    struct WorkerTask {
        Message<PaymentEvent> message;
        std::unique_ptr<AcknowledgmentHandle> ack_handle;
    };

    struct WorkerQueue {
        std::queue<WorkerTask> tasks;
        std::mutex mutex;
        std::condition_variable cv;
        std::thread thread;
        std::atomic<bool> running{true};
    };

    std::vector<std::unique_ptr<WorkerQueue>> workers_;
    size_t worker_count_;
    size_t max_queue_capacity_;
    BankingDomainService& domain_service_;
    ThreadSafeInbox& inbox_;
    std::atomic<size_t> total_in_flight_{0};

    void workerLoop(size_t worker_id) {
        auto& w = *workers_[worker_id];
        while (w.running) {
            WorkerTask task;
            {
                std::unique_lock<std::mutex> lock(w.mutex);
                w.cv.wait(lock, [&] { return !w.tasks.empty() || !w.running; });
                if (!w.running && w.tasks.empty()) break;
                if (w.tasks.empty()) continue;

                task = std::move(w.tasks.front());
                w.tasks.pop();
            }

            total_in_flight_--;

            // Крок 1: Перевірка ідемпотентності (Inbox)
            if (!inbox_.tryClaim(task.message.headers.id)) {
                std::cout << "  [Endpoint W" << worker_id << "] ДУБЛІКАТ повідомлення " 
                          << task.message.headers.id << " -> пропуск і швидкий ACK.\n";
                task.ack_handle->ack();
                continue;
            }

            // Крок 2: Виклик бізнес-сервісу
            try {
                domain_service_.processPayment(task.message.payload);
                task.ack_handle->ack();
            } catch (const std::invalid_argument& ex) {
                // Постійна помилка -> перенаправлення в мертву чергу (DLQ)
                std::cout << "  [Endpoint W" << worker_id << "] ОТРУЙНИЙ ПАКЕТ: " << ex.what() 
                          << " -> Переміщення в DLQ.\n";
                task.ack_handle->rejectToDlq(ex.what());
            } catch (const std::exception& ex) {
                // Тимчасова помилка -> повернення в чергу (NACK)
                std::cout << "  [Endpoint W" << worker_id << "] Збій обробки: " << ex.what() 
                          << " -> NACK з повтором.\n";
                task.ack_handle->nack(ex.what());
            }
        }
    }

public:
    KeyPartitionedDispatcher(size_t worker_count, size_t max_queue_capacity,
                             BankingDomainService& ds, ThreadSafeInbox& inbox)
        : worker_count_(worker_count), max_queue_capacity_(max_queue_capacity),
          domain_service_(ds), inbox_(inbox) {
        
        for (size_t i = 0; i < worker_count_; ++i) {
            auto w = std::make_unique<WorkerQueue>();
            w->thread = std::thread(&KeyPartitionedDispatcher::workerLoop, this, i);
            workers_.push_back(std::move(w));
        }
    }

    ~KeyPartitionedDispatcher() {
        stop();
    }

    bool dispatch(Message<PaymentEvent> msg, std::unique_ptr<AcknowledgmentHandle> handle) {
        // Хешування ключа партиції для прив'язки до одного воркера
        std::hash<std::string> hasher;
        size_t worker_idx = hasher(msg.headers.partition_key) % worker_count_;
        auto& w = *workers_[worker_idx];

        {
            std::lock_guard<std::mutex> lock(w.mutex);
            if (w.tasks.size() >= max_queue_capacity_) {
                return false; // Сигнал Backpressure: черга переповнена!
            }
            w.tasks.push(WorkerTask{std::move(msg), std::move(handle)});
        }
        total_in_flight_++;
        w.cv.notify_one();
        return true;
    }

    void stop() {
        for (auto& w : workers_) {
            w->running = false;
            w->cv.notify_all();
            if (w->thread.joinable()) {
                w->thread.join();
            }
        }
    }

    size_t getInFlightCount() const { return total_in_flight_.load(); }
};

// ── 6. КАНАЛЬНИЙ АДАПТЕР ТА ТОЧКА ВХОДУ (DEMO RUNNER) ──────────────────────
int main() {
    std::cout << "=== Запуск демонстрації асинхронного Message Endpoint ===\n\n";

    BankingDomainService domain_service;
    ThreadSafeInbox inbox;
    const size_t NUM_WORKERS = 3;
    const size_t QUEUE_CAPACITY = 100;

    KeyPartitionedDispatcher dispatcher(NUM_WORKERS, QUEUE_CAPACITY, domain_service, inbox);

    auto ack_callback = [](const std::string& msg_id, AckStatus status, const std::string& reason) {
        if (status == AckStatus::ACKED) {
            std::cout << "    -> [Broker Callback] ACK підтверджено для " << msg_id << "\n";
        } else if (status == AckStatus::DLQ_ROUTED) {
            std::cout << "    -> [Broker Callback] DLQ збережено для " << msg_id << " (Причина: " << reason << ")\n";
        } else if (status == AckStatus::NACKED) {
            std::cout << "    -> [Broker Callback] NACK для " << msg_id << " (Причина: " << reason << ")\n";
        }
    };

    // Сценарій 1: Послідовність подій для одного клієнта (Account#42)
    std::cout << "--- 1. Тест строгой послідовності для Account#42 ---\n";
    std::vector<Message<PaymentEvent>> stream = {
        {{"msg-001", "Account#42", "orders", 1000}, {"ord-1", "Account#42", 0, "CREATE"}},
        {{"msg-002", "Account#42", "orders", 1001}, {"ord-2", "Account#42", 50000, "DEPOSIT"}},
        {{"msg-003", "Account#42", "orders", 1002}, {"ord-3", "Account#42", 15000, "WITHDRAW"}},
        // Сценарій 2: Дублікат попереднього повідомлення
        {{"msg-002", "Account#42", "orders", 1003}, {"ord-2", "Account#42", 50000, "DEPOSIT"}},
        // Сценарій 3: Інший клієнт (Account#99) — обробляється паралельно
        {{"msg-004", "Account#99", "orders", 1004}, {"ord-4", "Account#99", 0, "CREATE"}},
        {{"msg-005", "Account#99", "orders", 1005}, {"ord-5", "Account#99", 30000, "DEPOSIT"}},
        // Сценарій 4: Отруйний пакет (нульова сума при списанні)
        {{"msg-006", "Account#42", "orders", 1006}, {"ord-6", "Account#42", 0, "WITHDRAW"}}
    };

    for (auto& msg : stream) {
        auto handle = std::make_unique<AcknowledgmentHandle>(msg.headers.id, ack_callback);
        std::string id = msg.headers.id;
        while (!dispatcher.dispatch(msg, std::move(handle))) {
            std::cout << "  [Backpressure] Черга заповнена, очікування 10 мс...\n";
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
            handle = std::make_unique<AcknowledgmentHandle>(id, ack_callback);
        }
    }

    // Очікування завершення обробки
    std::this_thread::sleep_for(std::chrono::milliseconds(300));

    std::cout << "\n--- Завершення роботи: Дренування буферів ---\n";
    dispatcher.stop();
    std::cout << "Всі воркери безпечно зупинені. Демонстрацію завершено успішно.\n";

    return 0;
}
