#include <mutex>
#include <condition_variable>
#include <chrono>

class EventFlag {
public:
    EventFlag() : ready_(false) {}

    bool wait(std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        return cv_.wait_for(lock, timeout, [this] {
            return ready_;
        });
    }

    void set() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            ready_ = true;
        }
        cv_.notify_all();
    }

    void reset() {
        std::lock_guard<std::mutex> lock(mutex_);
        ready_ = false;
    }

private:
    std::mutex mutex_;
    std::condition_variable cv_;
    bool ready_;
};
