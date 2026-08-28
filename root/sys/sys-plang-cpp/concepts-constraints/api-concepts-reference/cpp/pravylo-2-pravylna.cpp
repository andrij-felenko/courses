// НЕПРАВИЛЬНО: вимагає можливості створити rvalue-копію
template<typename T, typename... Args>
requires std::constructible_from<T, Args...>
T create_object(Args&&... args);

// ПРАВИЛЬНО: враховує категорії значень переданих аргументів
template<typename T, typename... Args>
requires std::constructible_from<T, Args&&...>
T create_object(Args&&... args) {
    return T(std::forward<Args>(args)...);
}
