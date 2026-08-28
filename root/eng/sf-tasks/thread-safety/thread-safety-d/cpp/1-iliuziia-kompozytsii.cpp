#include <optional>
#include <mutex>
#include <queue>

template <typename T>
class SafeQueue {
public:
    std::optional<T> try_pop() {
        std::lock_guard<std::mutex> guard(mutex_);
        if (data_.empty()) {
            return std::nullopt;
        }
        T item = std::move(data_.front());
        data_.pop();
        return item;
    }
private:
    std::mutex mutex_;
    std::queue<T> data_;
};
