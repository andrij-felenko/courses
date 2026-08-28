class HeavyDocument {
    std::string title;
    std::vector<std::string> pages;

    // Технічний кеш не повинен брати участь у порівнянні
    mutable uint64_t render_cache_id{0};

public:
    HeavyDocument(std::string t, std::vector<std::string> p)
        : title(std::move(t)), pages(std::move(p)) {}

    // Явне порівняння лише бізнес-полів
    friend auto operator<=>(const HeavyDocument& a, const HeavyDocument& b) noexcept {
        if (auto cmp = a.title <=> b.title; cmp != 0) return cmp;
        return a.pages <=> b.pages;
    }

    friend bool operator==(const HeavyDocument& a, const HeavyDocument& b) noexcept {
        return a.title == b.title && a.pages == b.pages;
    }
};
