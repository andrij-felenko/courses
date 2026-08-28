namespace std {
    // Тип функції обробника відмови виділення пам'яті
    using new_handler = void (*)();

    // Встановлює новий обробник і повертає попередній
    new_handler set_new_handler(new_handler new_p) noexcept;

    // Повертає поточний активний обробник (C++11)
    new_handler get_new_handler() noexcept;

    // Базовий виняток відмови виділення пам'яті
    class bad_alloc : public exception {
    public:
        bad_alloc() noexcept;
        bad_alloc(const bad_alloc&) noexcept;
        bad_alloc& operator=(const bad_alloc&) noexcept;
        virtual const char* what() const noexcept override;
    };

    // Виняток невідповідності розміру масиву (C++11)
    class bad_array_new_length : public bad_alloc {
    public:
        bad_array_new_length() noexcept;
        virtual const char* what() const noexcept override;
    };

    // Маркерний тип для non-throwing перевантажень
    struct nothrow_t { explicit nothrow_t() = default; };
    extern const nothrow_t nothrow;

    // Тип-перелік для передачі вирівнювання (C++17)
    enum class align_val_t : size_t {};
}
