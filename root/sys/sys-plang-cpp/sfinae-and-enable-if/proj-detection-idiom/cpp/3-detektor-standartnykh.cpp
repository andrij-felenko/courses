template<typename T, typename = void>
struct is_iterable_container : std::false_type {};

template<typename T>
struct is_iterable_container<T, std::void_t<
    decltype(std::declval<const T&>().begin()),
    decltype(std::declval<const T&>().end()),
    typename T::value_type
>> : std::true_type {};

template<typename T>
inline constexpr bool is_iterable_container_v = is_iterable_container<T>::value;
