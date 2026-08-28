namespace std {

template <typename R>
class shared_future {
public:
    constexpr shared_future() noexcept;
    shared_future(const shared_future& rhs) noexcept;
    shared_future(shared_future&& rhs) noexcept;
    shared_future(future<R>&& rhs) noexcept;
    ~shared_future();

    shared_future& operator=(const shared_future& rhs) noexcept;
    shared_future& operator=(shared_future&& rhs) noexcept;

    bool valid() const noexcept;

    // Зверніть увагу: get() повертає const R& для загального типу R
    const R& get() const;

    void wait() const;
    template <class Rep, class Period>
    future_status wait_for(const chrono::duration<Rep, Period>& timeout_duration) const;
    template <class Clock, class Duration>
    future_status wait_until(const chrono::time_point<Clock, Duration>& timeout_time) const;
};

// Спеціалізація для посилань
template <typename R>
class shared_future<R&> {
public:
    R& get() const;
};

// Спеціалізація для void
template <>
class shared_future<void> {
public:
    void get() const;
};

} // namespace std
