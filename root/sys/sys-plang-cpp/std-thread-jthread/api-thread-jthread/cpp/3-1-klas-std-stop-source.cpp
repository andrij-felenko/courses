// Створити нове джерело із власним stop_state
stop_source();

// Створити неактивне джерело без stop_state
explicit stop_source(std::nostopstate_t) noexcept;

// Конструктор та оператор переміщення
stop_source(stop_source&&) noexcept;
stop_source& operator=(stop_source&&) noexcept;

// Конструктор та оператор копіювання (збільшує ref-count)
stop_source(const stop_source&) noexcept;
stop_source& operator=(const stop_source&) noexcept;

// Запитати зупинку
bool request_stop() noexcept;

// Перевірити, чи надіслано сигнал зупинки
bool stop_requested() const noexcept;

// Перевірити, чи можлива зупинка
bool stop_possible() const noexcept;

// Отримати токен спостереження
std::stop_token get_token() const noexcept;
