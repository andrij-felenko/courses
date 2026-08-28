// Крок 1: Первинний шаблон (за замовчуванням властивість відсутня)
template<typename T, typename = void>
struct has_clone_method : std::false_type {};

// Крок 2: Часткова спеціалізація для валідного виразу
template<typename T>
struct has_clone_method<T, std::void_t<
    decltype(std::declval<const T&>().clone())
>> : std::true_type {};

// Зручний константний доступ (C++17)
template<typename T>
inline constexpr bool has_clone_method_v = has_clone_method<T>::value;
