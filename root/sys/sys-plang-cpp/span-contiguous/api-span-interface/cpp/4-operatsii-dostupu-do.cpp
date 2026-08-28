// Повертає посилання на i-й елемент (без перевірки меж у release)
constexpr reference operator[](size_type idx) const;

// Повертає посилання на перший та останній елемент
constexpr reference front() const;
constexpr reference back() const;

// Повертає вказівник на початок масиву у пам'яті
constexpr pointer data() const noexcept;

// Кількість елементів у зрізі
constexpr size_type size() const noexcept;

// Загальний розмір масиву у байтах (size() * sizeof(element_type))
constexpr size_type size_bytes() const noexcept;

// Перевірка чи порожній зріз (size() == 0)
[[nodiscard]] constexpr bool empty() const noexcept;
