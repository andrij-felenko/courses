template<typename T>
concept integral = std::is_integral_v<T>;

template<typename T>
concept signed_integral = std::integral<T> && std::is_signed_v<T>;

template<typename T>
concept unsigned_integral = std::integral<T> && !std::is_signed_v<T>;

template<typename T>
concept floating_point = std::is_floating_point_v<T>;
