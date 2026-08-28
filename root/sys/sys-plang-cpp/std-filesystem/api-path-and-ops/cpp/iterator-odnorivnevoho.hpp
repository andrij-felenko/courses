namespace std::filesystem {
    class directory_iterator {
    public:
        using iterator_category = std::input_iterator_tag;
        using value_type        = directory_entry;
        using difference_type   = std::ptrdiff_t;
        using pointer           = const directory_entry*;
        using reference         = const directory_entry&;

        directory_iterator() noexcept;
        explicit directory_iterator(const path& p);
        directory_iterator(const path& p, directory_options options);
        directory_iterator(const path& p, std::error_code& ec) noexcept;
        directory_iterator(const path& p, directory_options options, std::error_code& ec) noexcept;

        const directory_entry& operator*() const;
        const directory_entry* operator->() const;
        directory_iterator& operator++();
        directory_iterator& increment(std::error_code& ec) noexcept;

        bool operator==(const directory_iterator& rhs) const noexcept;
        bool operator!=(const directory_iterator& rhs) const noexcept;
    };
}
