#include <mutex>

class Document {
    std::string          text_;
    mutable std::once_flag once_;
    mutable Summary      cache_;

public:
    explicit Document(std::string text) : text_(std::move(text)) {}

    std::size_t word_count() const {
        std::call_once(once_, [this] { cache_ = compute_summary(text_); });
        return cache_.words;
    }
};
