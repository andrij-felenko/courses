template <class Clock, class Duration>
class time_point {
public:
    using clock = Clock;
    using duration = Duration;
    using rep = typename duration::rep;
    using period = typename duration::period;

    // Конструктори
    constexpr time_point(); // Ініціалізує точку часу значенням duration::zero() (Епоха)
    explicit constexpr time_point(const duration& d); // Точка часу зі зсувом d від епохи
    template <class Duration2>
    constexpr time_point(const time_point<clock, Duration2>& t);

    // Отримання тривалості від початку епохи
    constexpr duration time_since_epoch() const { return d_; }

    // Составні оператори
    constexpr time_point& operator+=(const duration& d) { d_ += d; return *this; }
    constexpr time_point& operator-=(const duration& d) { d_ -= d; return *this; }

    // Статичні межі
    static constexpr time_point min() noexcept { return time_point(duration::min()); }
    static constexpr time_point max() noexcept { return time_point(duration::max()); }
private:
    duration d_;
};
