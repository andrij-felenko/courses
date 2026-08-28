// Конкурентне оброблення результатів через потокобезпечну чергу
class SafeResultQueue {
private:
    std::queue<std::expected<TaskResult, TaskError>> queue_;
    mutable std::mutex mutex_;
public:
    void push(std::expected<TaskResult, TaskError> res) {
        std::lock_guard<std::mutex> lock(mutex_);
        queue_.push(std::move(res));
    }

    std::optional<std::expected<TaskResult, TaskError>> pop() {
        std::lock_guard<std::mutex> lock(mutex_);
        if (queue_.empty()) return std::nullopt;
        auto res = std::move(queue_.front());
        queue_.pop();
        return res;
    }
};
