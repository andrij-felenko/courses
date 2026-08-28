class BatchEventBuffer {
private:
    std::vector<UsageEvent> buffer_;
    size_t max_batch_size_;
    std::chrono::milliseconds max_delay_;
    std::chrono::steady_clock::time_point last_flush_;

public:
    BatchEventBuffer(size_t max_batch_size, std::chrono::milliseconds max_delay)
        : max_batch_size_(max_batch_size), max_delay_(max_delay), 
          last_flush_(std::chrono::steady_clock::now()) {
        buffer_.reserve(max_batch_size_);
    }

    // Додавання події в локальний буфер; повертає true, якщо потрібен негайний скид
    bool push(UsageEvent event) {
        buffer_.push_back(std::move(event));
        auto now = std::chrono::steady_clock::now();
        if (buffer_.size() >= max_batch_size_ || (now - last_flush_) >= max_delay_) {
            return true;
        }
        return false;
    }

    // Вилучення накопиченого пакета для атомарного запису в базу
    std::vector<UsageEvent> extract_batch() {
        std::vector<UsageEvent> batch;
        batch.swap(buffer_);
        buffer_.reserve(max_batch_size_);
        last_flush_ = std::chrono::steady_clock::now();
        return batch;
    }

    size_t pending_count() const { return buffer_.size(); }
};
