namespace std {
    struct once_flag {
        // Конструктор за замовчуванням (constexpr)
        constexpr once_flag() noexcept;

        // Копіювання суворо заборонено
        once_flag(const once_flag&) = delete;
        once_flag& operator=(const once_flag&) = delete;

        // Переміщення суворо заборонено
        once_flag(once_flag&&) = delete;
        once_flag& operator=(once_flag&&) = delete;

        // Тривіальний деструктор
        ~once_flag() = default;
    };
}
