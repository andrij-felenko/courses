template <class Duration>
class hh_mm_ss {
public:
    constexpr explicit hh_mm_ss(Duration d);

    constexpr bool is_negative() const noexcept;
    constexpr hours hours() const noexcept;
    constexpr minutes minutes() const noexcept;
    constexpr seconds seconds() const noexcept;
    constexpr precision subseconds() const noexcept;
    constexpr explicit operator precision() const noexcept;
    constexpr precision to_duration() const noexcept;
};
