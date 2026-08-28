class Document {
    std::string             text_;
    mutable std::mutex      m_;
    mutable Summary         cache_;
    mutable std::atomic<bool> ready_{false};

public:
    explicit Document(std::string text) : text_(std::move(text)) {}

    Document(const Document& other) {
        std::lock_guard lock(other.m_);          // джерело живе — його треба стерегти
        text_  = other.text_;
        cache_ = other.cache_;
        ready_.store(other.ready_.load(std::memory_order_relaxed),
                     std::memory_order_relaxed);
        // m_ — свіжий власний м'ютекс: новий об'єкт ще нікому не роздано
    }

    Document(Document&& other) noexcept
        : text_(std::move(other.text_)),
          cache_(std::move(other.cache_)),
          ready_(other.ready_.load(std::memory_order_relaxed)) {
        other.cache_ = Summary{};                          // джерело більше не має тексту —
        other.ready_.store(false, std::memory_order_relaxed);  // його кеш став брехнею
    }

    Document& operator=(const Document& other) {
        if (this == &other) return *this;        // обов'язково, і не заради швидкості
        std::scoped_lock lock(m_, other.m_);     // C++17: обидва разом, без дедлоку
        text_  = other.text_;
        cache_ = other.cache_;
        ready_.store(other.ready_.load(std::memory_order_relaxed),
                     std::memory_order_relaxed);
        return *this;
    }

    Document& operator=(Document&& other) noexcept {
        if (this == &other) return *this;
        text_  = std::move(other.text_);
        cache_ = std::move(other.cache_);
        ready_.store(other.ready_.load(std::memory_order_relaxed),
                     std::memory_order_relaxed);
        other.cache_ = Summary{};
        other.ready_.store(false, std::memory_order_relaxed);
        return *this;
    }

    ~Document() = default;

    // word_count(), digest() і fill() — без змін, як у версії 4
};
