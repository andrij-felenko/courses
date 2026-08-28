class stop_token {
public:
    // Конструктори та деструктор
    stop_token() noexcept;
    stop_token(const stop_token& other) noexcept;
    stop_token(stop_token&& other) noexcept;
    ~stop_token();

    // Оператори присвоєння
    stop_token& operator=(const stop_token& other) noexcept;
    stop_token& operator=(stop_token&& other) noexcept;

    // Модифікатори
    void swap(stop_token& other) noexcept;

    // Спостереження стану
    [[nodiscard]] bool stop_requested() const noexcept;
    [[nodiscard]] bool stop_possible() const noexcept;

    // Порівняння
    [[nodiscard]] friend bool operator==(const stop_token& lhs, const stop_token& rhs) noexcept;
};

// Нечленні функції обміну
void swap(stop_token& lhs, stop_token& rhs) noexcept;
