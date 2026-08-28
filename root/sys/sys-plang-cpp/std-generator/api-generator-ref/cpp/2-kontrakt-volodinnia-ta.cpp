// 1. Конструктор за замовчуванням створює порожній генератор
constexpr generator() noexcept : coroutine_(nullptr) {}

// 2. Конструктор копіювання вилучено (Copy Operations Deleted)
generator(const generator&) = delete;
generator& operator=(const generator&) = delete;

// 3. Конструктор переміщення передає дескриптор без виділення пам'яті
generator(generator&& rhs) noexcept
    : coroutine_(std::exchange(rhs.coroutine_, nullptr)) {}

// 4. Оператор присвоєння переміщенням знищує поточний кадр та забирає новий
generator& operator=(generator&& rhs) noexcept {
    if (this != std::addressof(rhs)) {
        if (coroutine_) {
            coroutine_.destroy();
        }
        coroutine_ = std::exchange(rhs.coroutine_, nullptr);
    }
    return *this;
}

// 5. Деструктор автоматично вивільняє кадр корутини у купі
~generator() {
    if (coroutine_) {
        coroutine_.destroy();
    }
}
