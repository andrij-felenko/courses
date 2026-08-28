#include <thread>
#include <stop_token>
#include <iostream>
#include <chrono>
#include <condition_variable>
#include <mutex>

class WorkerTask {
public:
    WorkerTask() {
        thread_ = std::jthread([this](std::stop_token st) {
            run(st);
        });
    }

    void request_stop() {
        thread_.request_stop();
        cv_.notify_all(); // Пробудження від сну
    }

private:
    void run(std::stop_token st) {
        std::stop_callback sc(st, [this]() {
            cv_.notify_all();
        });

        while (!st.stop_requested()) {
            std::unique_lock lock(mutex_);
            cv_.wait(lock, [&st]() {
                return st.stop_requested();
            });

            if (st.stop_requested()) break;
        }
        std::cout << "[CPP-WORKER] Потік штатно зупинився через stop_token\n";
    }

    std::mutex mutex_;
    std::condition_variable cv_;
    std::jthread thread_; // Автоматично викликає request_stop() та join() у деструкторі
};
