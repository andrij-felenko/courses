namespace std::this_thread {
    // Отримати ідентифікатор поточного потоку
    std::thread::id get_id() noexcept;

    // Добровільно віддати решту кванту часу CPU
    void yield() noexcept;

    // Заблокувати поточний потік на задану тривалість
    template <class Rep, class Period>
    void sleep_for(const std::chrono::duration<Rep, Period>& sleep_duration);

    // Заблокувати поточний потік до конкретного моменту часу
    template <class Clock, class Duration>
    void sleep_until(const std::chrono::time_point<Clock, Duration>& sleep_time);
}
