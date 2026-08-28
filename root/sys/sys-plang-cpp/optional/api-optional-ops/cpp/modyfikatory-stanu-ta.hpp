// Скидання стану у порожній (виклик деструктора T.~T() якщо заповнений)
void reset() noexcept;

// Конструювання об'єкта на місці (inplace construction)
template <class... Args>
T& emplace(Args&&... args);

template <class U, class... Args>
T& emplace(std::initializer_list<U> il, Args&&... args);

// Присвоєння
optional& operator=(nullopt_t) noexcept;
optional& operator=(const optional& rhs);
optional& operator=(optional&& rhs) noexcept(...);

template <class U = T>
optional& operator=(U&& rhs);

// Обмін вмістом
void swap(optional& rhs) noexcept(...);
