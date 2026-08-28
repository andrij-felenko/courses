namespace std {
    class nested_exception {
    public:
        nested_exception() noexcept;
        nested_exception(const nested_exception&) noexcept = default;
        nested_exception& operator=(const nested_exception&) noexcept = default;
        virtual ~nested_exception() = default;

        // Повертає збережений вкладений виняток
        exception_ptr nested_ptr() const noexcept;

        // Повторно кидає вкладений виняток
        [[noreturn]] void rethrow_nested() const;
    };

    // Створює вкладений виняток із поточного активного винятку
    template<class T>
    [[noreturn]] void throw_with_nested(T&& t);

    // Повторно кидає вкладений виняток, якщо об'єкт успадковує від std::nested_exception
    template<class E>
    void rethrow_if_nested(const E& e);
}
