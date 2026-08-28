namespace std::filesystem {
    class recursive_directory_iterator {
    public:
        using iterator_category = std::input_iterator_tag;
        using value_type        = directory_entry;

        recursive_directory_iterator() noexcept;
        explicit recursive_directory_iterator(const path& p);
        recursive_directory_iterator(const path& p, directory_options options);
        recursive_directory_iterator(const path& p, std::error_code& ec) noexcept;
        recursive_directory_iterator(const path& p, directory_options options, std::error_code& ec) noexcept;

        directory_options options() const;
        int depth() const;
        bool recursion_pending() const;

        void pop();
        void pop(std::error_code& ec);
        void disable_recursion_pending();

        const directory_entry& operator*() const;
        const directory_entry* operator->() const;
        recursive_directory_iterator& operator++();
        recursive_directory_iterator& increment(std::error_code& ec) noexcept;
    };
}
