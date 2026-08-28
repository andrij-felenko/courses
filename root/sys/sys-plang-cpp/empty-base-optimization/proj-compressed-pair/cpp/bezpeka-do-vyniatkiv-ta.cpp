template <typename T1, typename T2>
class noexcept_compressed_pair {
    COURSES_NO_UNIQUE_ADDRESS T1 first_{};
    COURSES_NO_UNIQUE_ADDRESS T2 second_{};

public:
    constexpr noexcept_compressed_pair() noexcept(
        std::is_nothrow_default_constructible_v<T1> &&
        std::is_nothrow_default_constructible_v<T2>) = default;

    constexpr noexcept_compressed_pair(noexcept_compressed_pair&& other) noexcept(
        std::is_nothrow_move_constructible_v<T1> &&
        std::is_nothrow_move_constructible_v<T2>)
        : first_{std::forward<T1>(other.first_)},
          second_{std::forward<T2>(other.second_)} {}

    constexpr noexcept_compressed_pair& operator=(noexcept_compressed_pair&& other) noexcept(
        std::is_nothrow_move_assignable_v<T1> &&
        std::is_nothrow_move_assignable_v<T2>) {
        first_ = std::forward<T1>(other.first_);
        second_ = std::forward<T2>(other.second_);
        return *this;
    }

    constexpr void swap(noexcept_compressed_pair& other) noexcept(
        std::is_nothrow_swappable_v<T1> &&
        std::is_nothrow_swappable_v<T2>) {
        using std::swap;
        swap(first_, other.first_);
        swap(second_, other.second_);
    }
};
