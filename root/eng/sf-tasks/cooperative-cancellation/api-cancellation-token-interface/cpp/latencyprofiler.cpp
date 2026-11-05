#include <iostream>
#include <atomic>
#include <condition_variable>
#include <mutex>
#include <thread>
#include <chrono>

// Клас профілювання та діагностики затримки скасування
class LatencyProfiler {
public:
    static void signal_start() noexcept {
        start_time_ = std::chrono::high_resolution_clock::now();
        std::cout << "[Profiler] Сигнал скасування подано (GPIO High).\n";
    }

    static void signal_end() noexcept {
        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time_).count();
        std::cout << "[Profiler] Зупинку завершено (GPIO Low). Виміряна затримка: " << duration << " мкс.\n";
    }

private:
    static inline std::chrono::high_resolution_clock::time_point start_time_;
};

// Джерело скасування з можливістю переривання блокуючого очікування
class InterruptibleCancellationTokenSource {
public:
    InterruptibleCancellationTokenSource() : cancelled_(false) {}

    void cancel() {
        {
            std::lock_guard<std::mutex> lock(cv_mutex_);
            cancelled_.store(true, std::memory_order_release);
        }
        LatencyProfiler::signal_start();
        cv_.notify_all(); // Розбудження блокованих потоків
    }

    [[nodiscard]] bool is_cancelled() const noexcept {
        return cancelled_.load(std::memory_order_acquire);
    }

    // Блокуюче очікування з підтримкою скасування
    template<typename Rep, typename Period>
    bool wait_for(const std::chrono::duration<Rep, Period>& rel_time) {
        std::unique_lock<std::mutex> lock(cv_mutex_);
        return cv_.wait_for(lock, rel_time, [this]() {
            return cancelled_.load(std::memory_order_acquire);
        });
    }

private:
    std::atomic<bool> cancelled_;
    std::mutex cv_mutex_;
    std::condition_variable cv_;
};

// Робоча задача з діагностикою та обробкою переривань
void profiled_worker(InterruptibleCancellationTokenSource& cts) {
    std::cout << "[Worker Thread] Запуск робочого циклу з контролем затримки.\n";

    for (int i = 0; i < 10; ++i) {
        // Перевірка очікування з таймаутом 100 мс
        if (cts.wait_for(std::chrono::milliseconds(100))) {
            std::cout << "[Worker Thread] Отримано сповіщення про скасування!\n";
            // Очищення ресурсів
            LatencyProfiler::signal_end();
            return;
        }
    }
    std::cout << "[Worker Thread] Робочий цикл успішно завершено.\n";
}
