namespace std {
    template <typename T, typename Allocator = std::allocator<T>>
    class vector {
    public:
        using size_type       = std::size_t;
        using reference       = T&;
        using const_reference = const T&;

        // Поточні показники заповненості
        size_type size() const noexcept;
        size_type capacity() const noexcept;
        size_type max_size() const noexcept;
        bool empty() const noexcept;

        // Зміна місткості та виділення надлишку
        void reserve(size_type new_cap);
        void shrink_to_fit();
        void resize(size_type count);
        void resize(size_type count, const value_type& value);
        void clear() noexcept;
    };
}
