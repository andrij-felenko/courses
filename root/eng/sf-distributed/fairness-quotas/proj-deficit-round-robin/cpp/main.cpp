#include <iostream>
#include <vector>
#include <deque>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <unordered_map>
#include <cstdint>

// Опис RPC-запиту
struct Request {
    uint64_t req_id{0};
    uint32_t tenant_id{0};
    uint32_t cost_units{1}; // Вартість у байтах або мікросекундах CPU
    std::string payload;
};

// Черга орендаря
class FlowQueue {
public:
    uint32_t tenant_id;
    uint32_t quantum;
    int32_t  deficit_counter{0};
    std::deque<Request> buffer;
    size_t   max_capacity{1024};

    FlowQueue(uint32_t id, uint32_t q, size_t cap = 1024)
        : tenant_id(id), quantum(q), max_capacity(cap) {}

    [[nodiscard]] bool is_empty() const noexcept {
        return buffer.empty();
    }

    [[nodiscard]] bool is_full() const noexcept {
        return buffer.size() >= max_capacity;
    }
};

// Потокобезпечний планувальник Deficit Round Robin
class DeficitRoundRobinScheduler {
public:
    DeficitRoundRobinScheduler() = default;

    void register_tenant(uint32_t tenant_id, uint32_t quantum) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (flows_.find(tenant_id) == flows_.end()) {
            flows_.emplace(tenant_id, std::make_shared<FlowQueue>(tenant_id, quantum));
        }
    }

    // Постановка запиту з контролем переповнення
    bool enqueue(Request req) {
        std::lock_guard<std::mutex> lock(mutex_);

        auto it = flows_.find(req.tenant_id);
        if (it == flows_.end() || it->second->is_full()) {
            return false; // Відхилення через невідомого клієнта або переповнення
        }

        auto& queue = it->second;
        bool was_empty = queue->is_empty();

        queue->buffer.push_back(std::move(req));

        if (was_empty) {
            // Потік повернувся з простою: скидаємо старий дефіцит і активуємо
            queue->deficit_counter = 0;
            active_flows_.push_back(queue);
            has_work_cv_.notify_one();
        }

        return true;
    }

    // Вибірка запиту за O(1)
    std::optional<Request> dequeue() {
        std::unique_lock<std::mutex> lock(mutex_);

        has_work_cv_.wait(lock, [this]() {
            return !active_flows_.empty() || shutdown_;
        });

        if (shutdown_ && active_flows_.empty()) {
            return std::nullopt;
        }

        while (!active_flows_.empty()) {
            auto current_queue = active_flows_.front();
            active_flows_.pop_front();

            // На початку раунду поповнюємо дефіцит на розмір кванта
            current_queue->deficit_counter += static_cast<int32_t>(current_queue->quantum);

            while (!current_queue->is_empty()) {
                const auto& head_req = current_queue->buffer.front();

                if (static_cast<int32_t>(head_req.cost_units) <= current_queue->deficit_counter) {
                    current_queue->deficit_counter -= static_cast<int32_t>(head_req.cost_units);
                    Request result = std::move(current_queue->buffer.front());
                    current_queue->buffer.pop_front();

                    // Якщо в черзі залишилися пакети — повертаємо її в активний список
                    if (!current_queue->is_empty()) {
                        active_flows_.push_front(current_queue);
                    } else {
                        // Черга порожня: обнуляємо дефіцит (Deficit Reset Rule)
                        current_queue->deficit_counter = 0;
                    }

                    return result;
                } else {
                    // Кванта недостатньо: зберігаємо дефіцит і відправляємо чергу в кінець кільця
                    break;
                }
            }

            if (!current_queue->is_empty()) {
                active_flows_.push_back(current_queue);
            } else {
                current_queue->deficit_counter = 0;
            }
        }

        return std::nullopt;
    }

    void shutdown() {
        std::lock_guard<std::mutex> lock(mutex_);
        shutdown_ = true;
        has_work_cv_.notify_all();
    }

private:
    std::mutex mutex_;
    std::condition_variable has_work_cv_;
    std::unordered_map<uint32_t, std::shared_ptr<FlowQueue>> flows_;
    std::deque<std::shared_ptr<FlowQueue>> active_flows_;
    bool shutdown_{false};
};
