// у публічній частині класу hw::Sample:

template <std::size_t I>
decltype(auto) get() & {
    static_assert(I < 2, "у hw::Sample дві частини");
    if constexpr      (I == 0) return voltage();   // double: обчислене значення
    else if constexpr (I == 1) return (tag_);      // std::string&
}

template <std::size_t I>
decltype(auto) get() const& {
    static_assert(I < 2, "у hw::Sample дві частини");
    if constexpr      (I == 0) return voltage();
    else if constexpr (I == 1) return (tag_);      // const std::string&
}

template <std::size_t I>
decltype(auto) get() && {
    static_assert(I < 2, "у hw::Sample дві частини");
    if constexpr      (I == 0) return voltage();
    else if constexpr (I == 1) return std::move(tag_);   // std::string&&
}
