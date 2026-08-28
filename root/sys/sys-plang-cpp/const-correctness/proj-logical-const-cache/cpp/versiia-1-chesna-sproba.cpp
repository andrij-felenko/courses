class Document {
    std::string text_;
    Summary     cache_;
    bool        ready_ = false;

public:
    explicit Document(std::string text) : text_(std::move(text)) {}

    std::size_t word_count() const {
        if (!ready_) {
            cache_ = compute_summary(text_);   // ✗
            ready_ = true;                     // ✗
        }
        return cache_.words;
    }
};
