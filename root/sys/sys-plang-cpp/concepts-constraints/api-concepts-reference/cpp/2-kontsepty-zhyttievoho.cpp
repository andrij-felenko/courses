// 1. Безпечне знищення об'єкта
template<typename T>
concept destructible = std::is_nothrow_destructible_v<T>;

// 2. Створення об'єкта з аргументами
template<typename T, typename... Args>
concept constructible_from = 
    std::destructible<T> && 
    std::is_constructible_v<T, Args...>;

// 3. Ініціалізація за замовчуванням
template<typename T>
concept default_initializable = 
    std::constructible_from<T> &&
    requires {
        T{};
        ::new (static_cast<void*>(nullptr)) T;
    } &&
    requires {
        T();
    };

// 4. Конструювання переміщенням
template<typename T>
concept move_constructible = 
    std::constructible_from<T, T> && 
    std::convertible_to<T, T>;

// 5. Конструювання копіюванням
template<typename T>
concept copy_constructible = 
    std::move_constructible<T> &&
    std::constructible_from<T, T&> && std::convertible_to<T&, T> &&
    std::constructible_from<T, const T&> && std::convertible_to<const T&, T> &&
    std::constructible_from<T, const T> && std::convertible_to<const T, T>;
