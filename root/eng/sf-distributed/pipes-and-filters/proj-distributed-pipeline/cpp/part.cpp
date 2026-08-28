#include <iostream>
#include <vector>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <memory>
#include <optional>
#include <chrono>
#include <string>
#include <atomic>

// ── Структури даних ────────────────────────────────────────────────────────
struct SecurityEvent {
    uint64_t event_id;
    std::string ip_address;
    uint16_t port;
    int payload_size;
    double risk_score{0.0};
    bool is_valid{true};
    std::chrono::steady_clock::time_point timestamp;
};

// ── 1. Обмежений потокобезпечний канал (Bounded Channel з протитиском) ─────
template <typename T>
class BoundedChannel {
public:
    explicit BoundedChannel(size_t capacity) : capacity_(capacity), closed_(false) {}

    // Відправка: блокує відправника, якщо черга заповнена (протитиск)
    bool push(T item) {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_not_full_.wait(lock, [this]() {
            return queue_.size() < capacity_ || closed_;
        });

        if (closed_) {
            return false;
        }

        queue_.push(std::move(item));
        cv_not_empty_.notify_one();
        return true;
    }

    // Отримання: блокує споживача, доки не з'явиться елемент
    std::optional<T> pop() {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_not_empty_.wait(lock, [this]() {
            return !queue_.empty() || closed_;
        });

        if (queue_.empty() && closed_) {
            return std::nullopt;
        }

        T item = std::move(queue_.front());
        queue_.pop();
        cv_not_full_.notify_one();
        return item;
    }

    void close() {
        std::lock_guard<std::mutex> lock(mutex_);
        closed_ = true;
        cv_not_empty_.notify_all();
        cv_not_full_.notify_all();
    }

    size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return queue_.size();
    }

private:
    const size_t capacity_;
    std::queue<T> queue_;
    mutable std::mutex mutex_;
    std::condition_variable cv_not_empty_;
    std::condition_variable cv_not_full_;
    bool closed_;
};

// ── 2. Фільтри конвеєра ───────────────────────────────────────────────────

// Фільтр 1: Декодування та початковий розбір
void stage_parser(BoundedChannel<SecurityEvent>& in_chan,
                  BoundedChannel<SecurityEvent>& out_chan,
                  std::atomic<uint64_t>& parsed_count) {
    while (auto item = in_chan.pop()) {
        auto event = std::move(*item);
        // Імітація легкої роботи з парсингу
        std::this_thread::sleep_for(std::chrono::microseconds(100));
        parsed_count.fetch_add(1, std::memory_order_relaxed);
        
        if (!out_chan.push(std::move(event))) {
            break;
        }
    }
    out_chan.close();
}

// Фільтр 2: Валідація схеми та санітизація
void stage_validator(BoundedChannel<SecurityEvent>& in_chan,
                     BoundedChannel<SecurityEvent>& out_chan,
                     std::atomic<uint64_t>& dropped_count) {
    while (auto item = in_chan.pop()) {
        auto event = std::move(*item);
        
        // Перевірка діапазону портів та розміру корисного навантаження
        if (event.port == 0 || event.payload_size > 65535 || event.payload_size < 0) {
            dropped_count.fetch_add(1, std::memory_order_relaxed);
            continue; // Відкидаємо пошкоджений пакет
        }

        std::this_thread::sleep_for(std::chrono::microseconds(150));
        
        if (!out_chan.push(std::move(event))) {
            break;
        }
    }
    out_chan.close();
}

// Фільтр 3: Оцінка рівня загроз (CPU-інтенсивний фільтр — вузьке місце)
void stage_scorer(BoundedChannel<SecurityEvent>& in_chan,
                  BoundedChannel<SecurityEvent>& out_chan,
                  std::atomic<uint64_t>& scored_count) {
    while (auto item = in_chan.pop()) {
        auto event = std::move(*item);
        
        // Розрахунок скорингу
        double score = 0.1;
        if (event.port == 22 || event.port == 3389) {
            score += 0.4; // Підозрілі адміністративні порти
        }
        if (event.payload_size > 4096) {
            score += 0.35;
        }
        event.risk_score = score;

        // Імітація складнішого аналізу
        std::this_thread::sleep_for(std::chrono::microseconds(400));
        scored_count.fetch_add(1, std::memory_order_relaxed);

        if (!out_chan.push(std::move(event))) {
            break;
        }
    }
    out_chan.close();
}

// Фільтр 4: Приймач результатів (Sink)
void stage_sink(BoundedChannel<SecurityEvent>& in_chan,
                std::atomic<uint64_t>& committed_count) {
    while (auto item = in_chan.pop()) {
        const auto& event = *item;
        committed_count.fetch_add(1, std::memory_order_relaxed);
        // Запис у сховище
        std::this_thread::sleep_for(std::chrono::microseconds(100));
    }
}

// ── Головна точка запуску конвеєра ─────────────────────────────────────────
int main() {
    const size_t TOTAL_EVENTS = 1000;
    const size_t BUFFER_CAPACITY = 64; // Обмежені буфери між стадіями

    // Створюємо канали між 4 стадіями
    BoundedChannel<SecurityEvent> chan_raw(BUFFER_CAPACITY);
    BoundedChannel<SecurityEvent> chan_parsed(BUFFER_CAPACITY);
    BoundedChannel<SecurityEvent> chan_validated(BUFFER_CAPACITY);
    BoundedChannel<SecurityEvent> chan_scored(BUFFER_CAPACITY);

    std::atomic<uint64_t> count_parsed{0};
    std::atomic<uint64_t> count_dropped{0};
    std::atomic<uint64_t> count_scored{0};
    std::atomic<uint64_t> count_committed{0};

    auto start_time = std::chrono::steady_clock::now();

    // Запускаємо потоки фільтрів
    std::thread th_parser(stage_parser, std::ref(chan_raw), std::ref(chan_parsed), std::ref(count_parsed));
    std::thread th_validator(stage_validator, std::ref(chan_parsed), std::ref(chan_validated), std::ref(count_dropped));
    std::thread th_scorer(stage_scorer, std::ref(chan_validated), std::ref(chan_scored), std::ref(count_scored));
    std::thread th_sink(stage_sink, std::ref(chan_scored), std::ref(count_committed));

    // Джерело (Producer): наповнює вхідний канал
    for (size_t i = 1; i <= TOTAL_EVENTS; ++i) {
        SecurityEvent ev;
        ev.event_id = i;
        ev.ip_address = "192.168.1." + std::to_string(i % 254 + 1);
        ev.port = (i % 20 == 0) ? 0 : (i % 5 == 0 ? 22 : 443); // Частина невалідних
        ev.payload_size = (i % 20 == 0) ? -10 : static_cast<int>(512 + (i * 37) % 8000);
        ev.timestamp = std::chrono::steady_clock::now();

        // Якщо вхідний канал переповнений, push блокується (протитиск)
        chan_raw.push(std::move(ev));
    }
    chan_raw.close();

    // Очікуємо завершення всіх стадій конвеєра
    th_parser.join();
    th_validator.join();
    th_scorer.join();
    th_sink.join();

    auto end_time = std::chrono::steady_clock::now();
    auto elapsed_ms = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count();

    std::cout << "=== Результати роботи конвеєра ===\n";
    std::cout << "Оброблено подій парсером:   " << count_parsed.load() << "\n";
    std::cout << "Відсіяно валідатором (збій): " << count_dropped.load() << "\n";
    std::cout << "Оцінено скорингом:          " << count_scored.load() << "\n";
    std::cout << "Записано в базу (Sink):     " << count_committed.load() << "\n";
    std::cout << "Загальний час виконання:    " << elapsed_ms << " мс\n";

    return 0;
}
