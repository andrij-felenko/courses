namespace std {
    class timed_mutex {
    public:
        timed_mutex();
        ~timed_mutex();

        timed_mutex(const timed_mutex&) = delete;
        timed_mutex& operator=(const timed_mutex&) = delete;

        void lock();
        bool try_lock();
        void unlock();

        template <class Rep, class Period>
        bool try_lock_for(const std::chrono::duration<Rep, Period>& timeout_duration);

        template <class Clock, class Duration>
        bool try_lock_until(const std::chrono::time_point<Clock, Duration>& timeout_time);
    };
}
