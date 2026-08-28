template<typename T, typename = void>
struct is_bidirectional_range : std::false_type {};

template<typename T>
struct is_bidirectional_range<T, std::void_t<
    decltype(std::declval<T>().begin()),
    decltype(std::declval<T>().end()),
    decltype(--std::declval<decltype(std::declval<T>().begin())&>()),
    typename T::value_type
>> : std::true_type {};
