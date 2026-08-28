namespace std {
    class error_category {
    public:
        constexpr error_category() noexcept;
        virtual ~error_category() noexcept;

        error_category(const error_category&) = delete;
        error_category& operator=(const error_category&) = delete;

        // Назва категорії помилок
        virtual const char* name() const noexcept = 0;

        // Повертає текстовий опис коду помилки
        virtual string message(int ev) const = 0;

        // Зіставляє системний код із загальним кодом
        virtual error_condition default_error_condition(int ev) const noexcept;

        // Порівняння категорій
        bool operator==(const error_category& rhs) const noexcept;
        bool operator!=(const error_category& rhs) const noexcept;
    };

    // Глобальні функції-фабрики стандартних категорій
    const error_category& system_category() noexcept;
    const error_category& generic_category() noexcept;
    const error_category& iostream_category() noexcept;
    const error_category& future_category() noexcept;
}
