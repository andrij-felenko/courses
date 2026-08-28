#include <mutex>

class Document {
    std::string        text_;
    mutable std::mutex m_;
    mutable Summary    cache_;
    mutable bool       ready_ = false;

    void ensure_locked() const {          // викликати ЛИШЕ під захопленим m_
        if (!ready_) { cache_ = compute_summary(text_); ready_ = true; }
    }

public:
    explicit Document(std::string text) : text_(std::move(text)) {}

    std::size_t word_count() const {
        std::lock_guard lock(m_);
        ensure_locked();
        return cache_.words;
    }
    std::string digest() const {
        std::lock_guard lock(m_);
        ensure_locked();
        return cache_.digest;             // копія під замком — назовні йде значення
    }
};
