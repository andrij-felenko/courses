// C++11–C++17: оператори ==, !=, <, <=, >, >=
template <typename... TTypes, typename... UTypes>
constexpr bool operator==(const tuple<TTypes...>& t, const tuple<UTypes...>& u);

template <typename... TTypes, typename... UTypes>
constexpr bool operator<(const tuple<TTypes...>& t, const tuple<UTypes...>& u);

// C++20: оператор трьохстороннього порівняння (<=>)
template <typename... TTypes, typename... UTypes>
constexpr auto operator<=>(const tuple<TTypes...>& t, const tuple<UTypes...>& u);
