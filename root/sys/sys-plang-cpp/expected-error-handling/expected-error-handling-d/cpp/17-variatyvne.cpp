template <typename F, typename... Args, typename E>
auto expected_apply(F&& f, std::expected<Args, E>... args) 
    -> std::expected<std::invoke_result_t<F, Args...>, E> 
{
    // Перевірка наявних значень в усіх аргументах
    bool all_ok = (args.has_value() && ...);
    if (!all_ok) {
        // Повертаємо першу знайдену помилку
        E err;
        ((!args.has_value() ? (err = args.error(), true) : false) || ...);
        return std::unexpected(err);
    }
    return std::invoke(std::forward<F>(f), std::move(*args)...);
}
