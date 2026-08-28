namespace hw {

// у класі додано публічні методи доступу:
//     std::string&       tag()       { return tag_; }
//     const std::string& tag() const { return tag_; }

template <std::size_t I> decltype(auto) get(Sample& s) {
    static_assert(I < 2, "у hw::Sample дві частини");
    if constexpr      (I == 0) return s.voltage();
    else if constexpr (I == 1) return s.tag();     // std::string&
}

template <std::size_t I> decltype(auto) get(const Sample& s) {
    static_assert(I < 2, "у hw::Sample дві частини");
    if constexpr      (I == 0) return s.voltage();
    else if constexpr (I == 1) return s.tag();     // const std::string&
}

template <std::size_t I> decltype(auto) get(Sample&& s) {
    static_assert(I < 2, "у hw::Sample дві частини");
    if constexpr      (I == 0) return s.voltage();
    else if constexpr (I == 1) return std::move(s.tag());
}

}  // namespace hw
