template <typename T>
struct is_expected : std::false_type {};

template <typename T, typename E>
struct is_expected<std::expected<T, E>> : std::true_type {};

template <typename T>
concept ExpectedType = is_expected<std::remove_cvref_t<T>>::value;

// Функція, що приймає лише результати типу std::expected
template <ExpectedType E>
void process_result(E&& res) {
    if (res) {
        // Обробка корисного навантаження
    }
}
