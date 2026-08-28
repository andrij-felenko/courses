// Отримання кількості альтернатив у варіанті на етапі компіляції
template <typename T> struct variant_size;

template <typename... Types>
struct variant_size<variant<Types...>> : std::integral_constant<size_t, sizeof...(Types)> {};

template <typename T>
inline constexpr size_t variant_size_v = variant_size<T>::value;

// Отримання типу альтернативи за її індексом I
template <size_t I, typename T> struct variant_alternative;

template <size_t I, typename T>
using variant_alternative_t = typename variant_alternative<I, T>::type;

// Константа порожнього або невалідного стану
inline constexpr size_t variant_npos = -1;
