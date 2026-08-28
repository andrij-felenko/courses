// 1. Default-конструктор (створює неактивний потік)
constexpr thread() noexcept;

// 2. Шаблонний конструктор запуску потоку
template <class Function, class... Args>
explicit thread(Function&& f, Args&&... args);

// 3. Конструктор переміщення
thread(thread&& other) noexcept;

// 4. Заборона копіювання
thread(const thread&) = delete;

// 5. Оператор переміщувального присвоєння
thread& operator=(thread&& other) noexcept;

// 6. Заборона присвоєння копіюванням
thread& operator=(const thread&) = delete;

// 7. Деструктор
~thread();
