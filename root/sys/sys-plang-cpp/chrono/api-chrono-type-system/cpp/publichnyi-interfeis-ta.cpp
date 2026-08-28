template <class Rep, class Period>
class duration {
public:
    using rep = Rep;
    using period = typename Period::type;

    // Конструктори
    constexpr duration() = default;
    template <class Rep2>
    explicit constexpr duration(const Rep2& r);
    template <class Rep2, class Period2>
    constexpr duration(const duration<Rep2, Period2>& d);

    // Селектори
    constexpr rep count() const { return r_; }

    // Статичні межові методи
    static constexpr duration zero() noexcept { return duration(Rep(0)); }
    static constexpr duration min() noexcept  { return duration(std::numeric_limits<Rep>::lowest()); }
    static constexpr duration max() noexcept  { return duration(std::numeric_limits<Rep>::max()); }

    // Унарні оператори
    constexpr duration operator+() const { return *this; }
    constexpr duration operator-() const { return duration(-r_); }

    // Інкремент та декремент
    constexpr duration& operator++() { ++r_; return *this; }
    constexpr duration operator++(int) { return duration(r_++); }
    constexpr duration& operator--() { --r_; return *this; }
    constexpr duration operator--(int) { return duration(r_--); }

    // Составні оператори присвоєння
    constexpr duration& operator+=(const duration& d) { r_ += d.count(); return *this; }
    constexpr duration& operator-=(const duration& d) { r_ -= d.count(); return *this; }
    constexpr duration& operator*=(const rep& rhs)   { r_ *= rhs; return *this; }
    constexpr duration& operator/=(const rep& rhs)   { r_ /= rhs; return *this; }
    constexpr duration& operator%=(const rep& rhs)   { r_ %= rhs; return *this; }
    constexpr duration& operator%=(const duration& d) { r_ %= d.count(); return *this; }
private:
    rep r_;
};
