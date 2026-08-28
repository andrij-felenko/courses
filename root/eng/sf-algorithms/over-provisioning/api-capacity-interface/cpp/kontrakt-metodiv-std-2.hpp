namespace std {
    template <
        typename Key,
        typename T,
        typename Hash = std::hash<Key>,
        typename KeyEqual = std::equal_to<Key>,
        typename Allocator = std::allocator<std::pair<const Key, T>>
    >
    class unordered_map {
    public:
        using size_type = std::size_t;

        // Робота з бакетами та заповненістю
        size_type bucket_count() const noexcept;
        size_type max_bucket_count() const noexcept;
        float load_factor() const noexcept;
        float max_load_factor() const noexcept;
        void max_load_factor(float ml);

        // Явне розширення надлишкових бакетів
        void rehash(size_type count);
        void reserve(size_type count);
    };
}
