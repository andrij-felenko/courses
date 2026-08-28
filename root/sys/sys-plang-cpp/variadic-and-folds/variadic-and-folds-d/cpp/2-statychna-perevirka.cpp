// Перевірка, що ВСІ типи в пакеті є цілочисельними
template <typename... Ts>
constexpr bool all_integral_v = (std::is_integral_v<Ts> && ...);

// Перевірка, що ХОЧА Б ОДИН тип є покажчиком
template <typename... Ts>
constexpr bool has_pointer_v = (std::is_pointer_v<Ts> || ...);

// Застосування у концептах C++20:
template <typename... Args>
    requires (std::is_integral_v<Args> && ...)
void process_integers_only(Args... args) {
    // Функція компілюється лише тоді, коли всі аргументи — цілі числа
}
