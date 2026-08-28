namespace std {

template <typename R>
class future {
public:
    constexpr future() noexcept;
    future(future&&) noexcept;
    future(const future&) = delete; // Копіювання заборонено!

    R get(); // Отримання результату (одноразово!)
    bool valid() const noexcept; // Перевірка валідності стану

    void wait() const; // Блокуюче очікування
    template <class Rep, class Period>
    future_status wait_for(const chrono::duration<Rep, Period>& timeout) const;
    template <class Clock, class Duration>
    future_status wait_until(const chrono::time_point<Clock, Duration>& timeout) const;
};

}
