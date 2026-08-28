#include <iostream>
#include <vector>
#include <array>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <atomic>
#include <span>
#include <numeric>

constexpr size_t BufferCapacity = 64;
constexpr size_t TestIterations = 10000;
constexpr size_t PacketSize = 8;

using Packet = std::array<uint8_t, PacketSize>;

class ThreadSafeRingBuffer {
public:
    explicit ThreadSafeRingBuffer(bool injectFlakiness)
        : injectFlakiness_(injectFlakiness) {}

    bool push(std::span<const uint8_t> src) {
        std::unique_lock<std::mutex> lock(mutex_);

        while (count_ + src.size() > BufferCapacity) {
            if (injectFlakiness_) {
                return false; // Симуляція втрати через переповнення
            }
            notFull_.wait(lock, [this, &src]() {
                return count_ + src.size() <= BufferCapacity;
            });
        }

        for (uint8_t byte : src) {
            buffer_[head_] = byte;
            head_ = (head_ + 1) % BufferCapacity;
        }
        count_ += src.size();

        notEmpty_.notify_one();
        return true;
    }

    bool pop(std::span<uint8_t> dst, std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);

        const bool ready = notEmpty_.wait_for(lock, timeout, [this, &dst]() {
            return count_ >= dst.size();
        });

        if (!ready) {
            return false; // Таймаут зчитування
        }

        for (uint8_t& byte : dst) {
            byte = buffer_[tail_];
            tail_ = (tail_ + 1) % BufferCapacity;
        }
        count_ -= dst.size();

        notFull_.notify_one();
        return true;
    }

private:
    std::array<uint8_t, BufferCapacity> buffer_{};
    size_t head_{0};
    size_t tail_{0};
    size_t count_{0};
    const bool injectFlakiness_{false};
    std::mutex mutex_;
    std::condition_variable notEmpty_;
    std::condition_variable notFull_;
};

struct TestResults {
    std::atomic<size_t> droppedPackets{0};
    std::atomic<size_t> checksumErrors{0};
};

void runStressBenchmark(bool injectFlakiness) {
    ThreadSafeRingBuffer ringBuffer(injectFlakiness);
    TestResults results;
    std::atomic<bool> stopFlag{false};

    auto producer = [&]() {
        Packet packet{};
        for (size_t seq = 0; seq < TestIterations && !stopFlag.load(); ++seq) {
            packet[0] = static_cast<uint8_t>(seq & 0xFF);
            packet[1] = static_cast<uint8_t>((seq >> 8) & 0xFF);
            for (size_t i = 2; i < PacketSize - 1; ++i) {
                packet[i] = static_cast<uint8_t>(i * 7);
            }
            uint8_t crc = 0;
            for (size_t i = 0; i < PacketSize - 1; ++i) {
                crc ^= packet[i];
            }
            packet[PacketSize - 1] = crc;

            if (!ringBuffer.push(packet)) {
                results.droppedPackets.fetch_add(1, std::memory_order_relaxed);
            }

            if (seq % 50 == 0) {
                std::this_thread::yield();
            }
        }
    };

    auto consumer = [&]() {
        Packet packet{};
        size_t received = 0;

        while (received < TestIterations && !stopFlag.load()) {
            if (!ringBuffer.pop(packet, std::chrono::milliseconds(50))) {
                break;
            }

            uint8_t crc = 0;
            for (size_t i = 0; i < PacketSize - 1; ++i) {
                crc ^= packet[i];
            }

            if (packet[PacketSize - 1] != crc) {
                results.checksumErrors.fetch_add(1, std::memory_order_relaxed);
            }
            received++;
        }
    };

    std::thread prodThread(producer);
    std::thread consThread(consumer);

    prodThread.join();
    consThread.join();

    std::cout << "  - Втрачено пакетів: " << results.droppedPackets.load() << "\n";
    std::cout << "  - Помилок контрольної суми: " << results.checksumErrors.load() << "\n";
}

int main() {
    std::cout << "=== Запуск C++ стрес-тесту буфера на 10000 ітерацій ===\n";

    std::cout << "Результати нестабільного режиму (симуляція гонки):\n";
    runStressBenchmark(true);

    std::cout << "Результати захищеного детермінованого режиму:\n";
    runStressBenchmark(false);

    std::cout << "СТАТУС: ТЕСТ ЗАВЕРШЕНО\n";
    return 0;
}
