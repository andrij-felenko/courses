class stop_source {
public:
    // Конструктори та деструктор
    stop_source();
    explicit stop_source(std::nostopstate_t) noexcept;
    stop_source(const stop_source& other) noexcept;
    stop_source(stop_source&& other) noexcept;
    ~stop_source();

    // Оператори присвоєння
    stop_source& operator=(const stop_source& other) noexcept;
    stop_source& operator=(stop_source&& other) noexcept;

    // Модифікатори
    void swap(stop_source& other) noexcept;
    bool request_stop() noexcept;

    // Спостереження стану
    [[nodiscard]] stop_token get_token() const noexcept;
    [[nodiscard]] bool stop_requested() const noexcept;
    [[nodiscard]] bool stop_possible() const noexcept;

    // Порівняння
    [[nodiscard]] friend bool operator==(const stop_source& lhs, const stop_source& rhs) noexcept;
};

// Нечленні функції обміну
void swap(stop_source& lhs, stop_source& rhs) noexcept;
