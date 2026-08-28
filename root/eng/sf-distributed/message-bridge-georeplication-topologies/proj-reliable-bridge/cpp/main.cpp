#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <deque>
#include <unordered_set>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <chrono>
#include <memory>
#include <atomic>
#include <optional>
#include <sstream>

// ── 1. Структура метаданих та конверта повідомлення ──────────────────────────
struct BridgeMessage {
    uint64_t msg_id{0};
    uint64_t source_offset{0};
    uint32_t origin_cluster_id{0};
    std::vector<uint32_t> hop_path;
    std::string payload;

    [[nodiscard]] std::string format_hops() const {
        std::ostringstream oss;
        oss << "[";
        for (size_t i = 0; i < hop_path.size(); ++i) {
            if (i > 0) oss << " -> ";
            oss << "0x" << std::hex << hop_path[i] << std::dec;
        }
        oss << "]";
        return oss.str();
    }
};

// ── 2. Потокобезпечний буфер з обмеженою ємністю та протитиском ──────────────
class BoundedBridgeQueue {
public:
    explicit BoundedBridgeQueue(size_t max_capacity)
        : max_capacity_(max_capacity), is_shutdown_(false) {}

    // Додавання повідомлення: блокує споживача при заповненні буфера (протитиск)
    bool push(BridgeMessage msg, std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        bool space_available = not_full_cv_.wait_for(lock, timeout, [this]() {
            return queue_.size() < max_capacity_ || is_shutdown_;
        });

        if (is_shutdown_ || !space_available) {
            return false;
        }

        queue_.push_back(std::move(msg));
        not_empty_cv_.notify_one();
        return true;
    }

    // Витягування повідомлення для відправки в цільовий брокер
    std::optional<BridgeMessage> pop(std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        bool item_available = not_empty_cv_.wait_for(lock, timeout, [this]() {
            return !queue_.empty() || is_shutdown_;
        });

        if (queue_.empty()) {
            return std::nullopt;
        }

        BridgeMessage msg = std::move(queue_.front());
        queue_.pop_front();
        not_full_cv_.notify_one();
        return msg;
    }

    void shutdown() {
        std::unique_lock<std::mutex> lock(mutex_);
        is_shutdown_ = true;
        not_empty_cv_.notify_all();
        not_full_cv_.notify_all();
    }

    [[nodiscard]] size_t size() const {
        std::unique_lock<std::mutex> lock(mutex_);
        return queue_.size();
    }

private:
    const size_t max_capacity_;
    std::deque<BridgeMessage> queue_;
    mutable std::mutex mutex_;
    std::condition_variable not_empty_cv_;
    std::condition_variable not_full_cv_;
    bool is_shutdown_;
};

// ── 3. Моделювання зовнішніх брокерів (Джерело та Ціль) ─────────────────────
class MockSourceBroker {
public:
    explicit MockSourceBroker(uint32_t cluster_id) : cluster_id_(cluster_id), current_offset_(0) {}

    std::optional<BridgeMessage> fetch_next() {
        if (current_offset_ >= 6) {
            return std::nullopt; // Кінець тестового потоку
        }

        BridgeMessage msg;
        msg.msg_id = 1000 + current_offset_;
        msg.source_offset = current_offset_++;
        
        // Симуляція відлуння (повідомлення 3 прийшло з цільового кластера 0x02)
        if (msg.source_offset == 3) {
            msg.origin_cluster_id = 0x02;
            msg.hop_path = {0x02, cluster_id_};
            msg.payload = "{\"event\":\"order_echo_test\",\"id\":404}";
        } else {
            msg.origin_cluster_id = cluster_id_;
            msg.hop_path = {cluster_id_};
            msg.payload = "{\"event\":\"order_created\",\"amount\":" + std::to_string(msg.source_offset * 150) + "}";
        }

        return msg;
    }

    void commit_offset(uint64_t offset) {
        std::lock_guard<std::mutex> lock(commit_mutex_);
        last_committed_offset_ = offset;
        std::cout << "  [Джерело 0x" << std::hex << cluster_id_ << std::dec 
                  << "] Офсет " << offset << " успішно ЗАФІКСОВАНО (Source Ack)\n";
    }

    [[nodiscard]] uint64_t get_committed_offset() const {
        std::lock_guard<std::mutex> lock(commit_mutex_);
        return last_committed_offset_;
    }

private:
    uint32_t cluster_id_;
    uint64_t current_offset_;
    uint64_t last_committed_offset_{0};
    mutable std::mutex commit_mutex_;
};

class MockTargetBroker {
public:
    explicit MockTargetBroker(uint32_t cluster_id) : cluster_id_(cluster_id) {}

    // Запис повідомлення в цільовий лог
    bool produce(const BridgeMessage& msg) {
        // Симуляція мережевої затримки запису на диск / реплікації
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
        std::cout << "  [Ціль 0x" << std::hex << cluster_id_ << std::dec 
                  << "] Записано msg_id=" << msg.msg_id 
                  << " (Hops: " << msg.format_hops() << ")\n";
        return true;
    }

private:
    uint32_t cluster_id_;
};

// ── 4. Ядро моста повідомлень (Message Bridge Core) ──────────────────────────
class MessageBridge {
public:
    MessageBridge(uint32_t bridge_id, uint32_t target_cluster_id,
                  MockSourceBroker& source, MockTargetBroker& target, size_t buffer_size)
        : bridge_id_(bridge_id),
          target_cluster_id_(target_cluster_id),
          source_broker_(source),
          target_broker_(target),
          queue_(buffer_size),
          running_(false),
          forwarded_count_(0),
          dropped_loops_count_(0) {}

    ~MessageBridge() {
        stop();
    }

    void start() {
        running_ = true;
        consumer_thread_ = std::thread(&MessageBridge::consume_worker, this);
        dispatcher_thread_ = std::thread(&MessageBridge::dispatch_worker, this);
    }

    void stop() {
        if (!running_.exchange(false)) return;

        queue_.shutdown();
        if (consumer_thread_.joinable()) consumer_thread_.join();
        if (dispatcher_thread_.joinable()) dispatcher_thread_.join();
    }

    [[nodiscard]] size_t get_forwarded_count() const { return forwarded_count_.load(); }
    [[nodiscard]] size_t get_dropped_loops_count() const { return dropped_loops_count_.load(); }

private:
    void consume_worker() {
        while (running_) {
            auto msg_opt = source_broker_.fetch_next();
            if (!msg_opt) {
                // Джерело тимчасово порожнє
                std::this_thread::sleep_for(std::chrono::milliseconds(30));
                break; // У тестовому сценарії завершуємо після вичитки
            }

            BridgeMessage msg = std::move(*msg_opt);

            // Крок А: Перевірка на циклічну петлю (Loop Detection)
            if (detect_cycle(msg)) {
                std::cout << "  [Міст] ⚠️ ВИЯВЛЕНО ПЕТЛЮ у msg_id=" << msg.msg_id 
                          << " (Шлях: " << msg.format_hops() << ") -> ВІДКИДАННЯ\n";
                // Фіксуємо офсет у джерелі, щоб не зависати на відкинутому повідомленні
                source_broker_.commit_offset(msg.source_offset);
                dropped_loops_count_++;
                continue;
            }

            // Крок Б: Додаємо цільовий кластер у шлях передачі
            msg.hop_path.push_back(target_cluster_id_);

            // Крок В: Запис у внутрішній буфер (із протитиском)
            while (running_) {
                if (queue_.push(std::move(msg), std::chrono::milliseconds(50))) {
                    break;
                }
            }
        }
    }

    void dispatch_worker() {
        while (running_ || queue_.size() > 0) {
            auto msg_opt = queue_.pop(std::chrono::milliseconds(50));
            if (!msg_opt) {
                if (!running_) break;
                continue;
            }

            const BridgeMessage& msg = *msg_opt;

            // Крок Г: Відправка в цільовий брокер
            bool write_ok = target_broker_.produce(msg);

            // Крок Ґ: Подвійне підтвердження (Dual Ack)
            if (write_ok) {
                // Лише після успішного підтвердження від цілі фіксуємо офсет на джерелі
                source_broker_.commit_offset(msg.source_offset);
                forwarded_count_++;
            } else {
                std::cerr << "  [Міст] ✗ Помилка запису в ціль msg_id=" << msg.msg_id << "\n";
            }
        }
    }

    [[nodiscard]] bool detect_cycle(const BridgeMessage& msg) const {
        for (uint32_t hop : msg.hop_path) {
            if (hop == target_cluster_id_) {
                return true; // Цільовий кластер уже бачив це повідомлення
            }
        }
        return false;
    }

    uint32_t bridge_id_;
    uint32_t target_cluster_id_;
    MockSourceBroker& source_broker_;
    MockTargetBroker& target_broker_;
    BoundedBridgeQueue queue_;
    std::atomic<bool> running_;
    std::thread consumer_thread_;
    std::thread dispatcher_thread_;
    std::atomic<size_t> forwarded_count_;
    std::atomic<size_t> dropped_loops_count_;
};

// ── 5. Демонстраційний сценарій роботи моста ─────────────────────────────────
int main() {
    std::cout << "=== ЗАПУСК МОСТА ПОВІДОМЛЕНЬ (C++20 Pipeline) ===\n";
    const uint32_t CLUSTER_EU = 0x01;
    const uint32_t CLUSTER_US = 0x02;

    MockSourceBroker source_eu(CLUSTER_EU);
    MockTargetBroker target_us(CLUSTER_US);

    {
        MessageBridge bridge(101, CLUSTER_US, source_eu, target_us, 500);
        bridge.start();

        // Очікуємо обробки всіх повідомлень конвеєром
        std::this_thread::sleep_for(std::chrono::milliseconds(300));
        bridge.stop();

        std::cout << "\n=== ПІДСУМОК РОБОТИ МОСТА ===\n";
        std::cout << "Успішно ретрансльовано: " << bridge.get_forwarded_count() << " повідомлень\n";
        std::cout << "Відсіяно циклічних петель: " << bridge.get_dropped_loops_count() << "\n";
    }

    return 0;
}
