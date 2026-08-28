class Document {
    std::string text_;
    mutable std::mutex m_;
    mutable std::optional<std::size_t> words_;
public:
    std::size_t word_count() const {
        std::lock_guard lock(m_);
        if (!words_) words_ = count_words(text_);
        return *words_;
    }
};
