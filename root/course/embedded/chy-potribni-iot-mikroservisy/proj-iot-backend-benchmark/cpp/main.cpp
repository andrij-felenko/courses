#include <iostream>
#include <vector>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <memory>
#include <span>
#include <cstring>
#include <atomic>
#include <sys/socket.h>
#include <unistd.h>

// 1. Структура телеметричного пакета (32 байти)
struct TelemetryRecord {
    uint64_t device_id;
    uint64_t timestamp_ms;
    float voltage;
    float current;
    float active_power;
    uint32_t status_flags;
};

// 2. Внутрішньопроцесна черга з нульовим копіюванням (In-Memory Queue)
class InProcessQueue {
public:
    void push(const TelemetryRecord& record) {
        std::lock_guard<std::mutex> lock(mtx_);
        queue_.push(record);
        cv_.notify_one();
    }

    bool pop(TelemetryRecord& out_record) {
        std::unique_lock<std::mutex> lock(mtx_);
        cv_.wait(lock, [this]() { return !queue_.empty() || finished_; });
        if (queue_.empty() && finished_) {
            return false;
        }
        out_record = queue_.front();
        queue_.pop();
        return true;
    }

    void finish() {
        std::lock_guard<std::mutex> lock(mtx_);
        finished_ = true;
        cv_.notify_all();
    }

private:
    std::queue<TelemetryRecord> queue_;
    std::mutex mtx_;
    std::condition_variable cv_;
    bool finished_ = false;
};

// 3. Бенчмарк In-Memory модульного моноліту
void benchmark_in_process(const size_t total_messages) {
    InProcessQueue queue;
    std::atomic<uint64_t> processed_count{0};

    auto start_time = std::chrono::high_resolution_clock::now();

    // Споживач (Consumer / Rules Engine)
    std::jthread consumer([&queue, &processed_count]() {
        TelemetryRecord rec;
        while (queue.pop(rec)) {
            // Моделювання легкої перевірки уставки (Rules Engine)
            if (rec.voltage > 250.0f) {
                // Аварійне перевищення напруги
            }
            processed_count.fetch_add(1, std::memory_order_relaxed);
        }
    });

    // Виробник (Producer / Ingestion Gateway)
    for (size_t i = 0; i < total_messages; ++i) {
        TelemetryRecord record{
            .device_id = 100000 + (i % 5000),
            .timestamp_ms = 1724700000000ULL + i,
            .voltage = 230.5f + static_cast<float>(i % 20) * 0.1f,
            .current = 5.2f,
            .active_power = 1198.6f,
            .status_flags = 0x01
        };
        queue.push(record);
    }
    queue.finish();
    consumer.join();

    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> elapsed = end_time - start_time;

    double msg_per_sec = static_cast<double>(total_messages) / (elapsed.count() / 1000.0);
    std::cout << "[In-Memory Monolith] Обробка " << total_messages 
              << " подій зайняла: " << elapsed.count() << " мс ("
              << static_cast<uint64_t>(msg_per_sec) << " msg/sec)\n";
}

// 4. Бенчмарк міжпроцесного сокета (Network IPC / Microservices emulation)
void benchmark_socket_rpc(const size_t total_messages) {
    int sv[2];
    if (socketpair(AF_UNIX, SOCK_STREAM, 0, sv) < 0) {
        std::cerr << "Помилка створення socketpair\n";
        return;
    }

    auto start_time = std::chrono::high_resolution_clock::now();

    // Споживач через сокет (Worker Process)
    std::jthread consumer([sock = sv[1], total_messages]() {
        TelemetryRecord rec;
        size_t count = 0;
        while (count < total_messages) {
            ssize_t bytes_read = ::read(sock, &rec, sizeof(TelemetryRecord));
            if (bytes_read <= 0) break;
            count += static_cast<size_t>(bytes_read) / sizeof(TelemetryRecord);
        }
        ::close(sock);
    });

    // Виробник через сокет (Gateway Process)
    for (size_t i = 0; i < total_messages; ++i) {
        TelemetryRecord record{
            .device_id = 100000 + (i % 5000),
            .timestamp_ms = 1724700000000ULL + i,
            .voltage = 230.5f + static_cast<float>(i % 20) * 0.1f,
            .current = 5.2f,
            .active_power = 1198.6f,
            .status_flags = 0x01
        };
        ::write(sv[0], &record, sizeof(TelemetryRecord));
    }
    ::close(sv[0]);
    consumer.join();

    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> elapsed = end_time - start_time;

    double msg_per_sec = static_cast<double>(total_messages) / (elapsed.count() / 1000.0);
    std::cout << "[Socket IPC Microservices] Обробка " << total_messages 
              << " подій зайняла: " << elapsed.count() << " мс ("
              << static_cast<uint64_t>(msg_per_sec) << " msg/sec)\n";
}

int main() {
    const size_t MSG_COUNT = 100000;
    std::cout << "Старт бенчмарку навантаження (" << MSG_COUNT << " повідомлень)...\n";
    benchmark_in_process(MSG_COUNT);
    benchmark_socket_rpc(MSG_COUNT);
    return 0;
}
