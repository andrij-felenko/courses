// 1. Перевірка наявності значення
constexpr bool has_value() const noexcept;
constexpr explicit operator bool() const noexcept;

// 2. Розгортання без перевірки (Unchecked Access — швидкий доступ, O(1), noexcept)
constexpr const T& operator*() const& noexcept;
constexpr T& operator*() & noexcept;
constexpr const T&& operator*() const&& noexcept;
constexpr T&& operator*() && noexcept;

constexpr const T* operator->() const noexcept;
constexpr T* operator->() noexcept;

// 3. Розгортання з перевіркою (Checked Access — кидає bad_optional_access)
constexpr const T& value() const&;
constexpr T& value() &;
constexpr const T&& value() const&&;
constexpr T&& value() &&;

// 4. Безпечне розгортання із дефолтом
template <class U>
constexpr T value_or(U&& default_value) const&;

template <class U>
constexpr T value_or(U&& default_value) &&;
