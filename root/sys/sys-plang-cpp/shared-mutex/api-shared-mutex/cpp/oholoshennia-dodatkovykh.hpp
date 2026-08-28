namespace std {
    class shared_timed_mutex {
    public:
        // Базові методи lock(), try_lock(), unlock(), lock_shared(), try_lock_shared(), unlock_shared()

        // Блокування на запис із граничним часом
        template <class Rep, class Period>
        bool try_lock_for(const std::chrono::duration<Rep, Period>& timeout_duration);

        template <class Clock, class Duration>
        bool try_lock_until(const std::chrono::time_point<Clock, Duration>& timeout_time);

        // Блокування на читання з граничним часом
        template <class Rep, class Period>
        bool try_lock_shared_for(const std::chrono::duration<Rep, Period>& timeout_duration);

        template <class Clock, class Duration>
        bool try_lock_shared_until(const std::chrono::time_point<Clock, Duration>& timeout_time);
    };
}
