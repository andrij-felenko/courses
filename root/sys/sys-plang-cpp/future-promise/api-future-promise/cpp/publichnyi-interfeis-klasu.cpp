namespace std {

template <typename R>
class future {
public:
    // 1. Конструктори та деструктор
    constexpr future() noexcept;
    future(future&& rhs) noexcept;
    future(const future&) = delete;
    ~future();

    // 2. Оператори присвоєння
    future& operator=(const future&) = delete;
    future& operator=(future&& rhs) noexcept;

    // 3. Конвертація у shared_future
    shared_future<R> share() noexcept;

    // 4. Отримання результату
    R get(); // Для первинного шаблону R
             // Для R& повертає R&
             // Для void повертає void

    // 5. Перевірка валідності
    bool valid() const noexcept;

    // 6. Блокуюче очікування
    void wait() const;
    
    template <typename Rep, typename Period>
    future_status wait_for(const chrono::duration<Rep, Period>& timeout_duration) const;
    
    template <typename Clock, typename Duration>
    future_status wait_until(const chrono::time_point<Clock, Duration>& timeout_time) const;
};

} // namespace std
