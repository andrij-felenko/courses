#include <atomic>
#include <mutex>

class Document {
    std::string             text_;
    mutable std::mutex      m_;
    mutable Summary         cache_;
    mutable std::atomic<bool> ready_{false};

    void fill() const {
        std::lock_guard lock(m_);
        if (!ready_.load(std::memory_order_relaxed)) {   // під замком — досить relaxed
            cache_ = compute_summary(text_);
            ready_.store(true, std::memory_order_release);
        }
    }

public:
    explicit Document(std::string text) : text_(std::move(text)) {}

    std::size_t word_count() const {
        if (!ready_.load(std::memory_order_acquire)) fill();
        return cache_.words;
    }
    std::string digest() const {
        if (!ready_.load(std::memory_order_acquire)) fill();
        return cache_.digest;
    }
};
