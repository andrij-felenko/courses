namespace std {
    template <class Mutex>
    class unique_lock {
    public:
        using mutex_type = Mutex;

        unique_lock() noexcept;
        explicit unique_lock(mutex_type& m);
        unique_lock(mutex_type& m, defer_lock_t) noexcept;
        unique_lock(mutex_type& m, try_to_lock_t);
        unique_lock(mutex_type& m, adopt_lock_t);

        template <class Rep, class Period>
        unique_lock(mutex_type& m, const std::chrono::duration<Rep, Period>& timeout_duration);

        ~unique_lock();

        unique_lock(const unique_lock&) = delete;
        unique_lock& operator=(const unique_lock&) = delete;

        unique_lock(unique_lock&& u) noexcept;
        unique_lock& operator=(unique_lock&& u) noexcept;

        void lock();
        bool try_lock();

        template <class Rep, class Period>
        bool try_lock_for(const std::chrono::duration<Rep, Period>& timeout_duration);

        void unlock();

        bool owns_lock() const noexcept;
        explicit operator bool() const noexcept;

        mutex_type* release() noexcept;
        mutex_type* mutex() const noexcept;
    };
}
