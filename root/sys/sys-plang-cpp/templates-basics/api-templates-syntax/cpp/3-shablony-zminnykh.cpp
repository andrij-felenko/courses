// Параметризована константа
template <typename T>
constexpr T golden_ratio = T(1.61803398874989484820458683436563811772L);

// Використання:
float  phi_f = golden_ratio<float>;   // Точність single-precision
double phi_d = golden_ratio<double>;  // Точність double-precision

// Скорочення для стандартних рис типів (Type Traits)
template <typename T>
inline constexpr bool is_integral_v = std::is_integral<T>::value;

template <typename From, typename To>
inline constexpr bool is_convertible_v = std::is_convertible<From, To>::value;
