class Document {
    std::string     text_;
    mutable Summary cache_;
    mutable bool    ready_ = false;

public:
    explicit Document(std::string text) : text_(std::move(text)) {}

    std::size_t word_count() const {
        if (!ready_) { cache_ = compute_summary(text_); ready_ = true; }
        return cache_.words;
    }
    std::string digest() const {
        if (!ready_) { cache_ = compute_summary(text_); ready_ = true; }
        return cache_.digest;
    }
};
