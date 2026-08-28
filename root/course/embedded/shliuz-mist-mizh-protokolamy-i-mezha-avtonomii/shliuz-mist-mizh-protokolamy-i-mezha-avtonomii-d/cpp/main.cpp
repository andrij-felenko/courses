#include <string>
#include <deque>
#include <mutex>
#include <optional>
#include <chrono>

struct TelemetryEntry {
    std::string topic;
    std::string payload;
    std::chrono::system_clock::time_point timestamp;
};

/* Ідіоматичний потокобезпечний буфер з витісненням застарілих даних (RAII) */
class SafeTelemetryRing {
public:
    explicit SafeTelemetryRing(size_t max_size) : max_size_(max_size) {}

    void pushOverwrite(TelemetryEntry item) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (queue_.size() >= max_size_) {
            queue_.pop_front(); // Витіснення найстарішого
        }
        queue_.push_back(std::move(item));
    }

    std::optional<TelemetryEntry> pop() {
        std::lock_guard<std::mutex> lock(mutex_);
        if (queue_.empty()) {
            return std::nullopt;
        }
        auto item = std::move(queue_.front());
        queue_.pop_front();
        return item;
    }

    [[nodiscard]] size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return queue_.size();
    }

private:
    const size_t max_size_;
    std::deque<TelemetryEntry> queue_;
    mutable std::mutex mutex_;
};
