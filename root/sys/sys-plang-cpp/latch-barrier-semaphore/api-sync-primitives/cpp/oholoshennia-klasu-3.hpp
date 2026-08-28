namespace std {
    template<ptrdiff_t LeastMaxValue = /* implementation-defined */>
    class counting_semaphore {
    public:
        static constexpr ptrdiff_t max() noexcept;

        constexpr explicit counting_semaphore(ptrdiff_t desired);
        ~counting_semaphore();

        counting_semaphore(const counting_semaphore&) = delete;
        counting_semaphore& operator=(const counting_semaphore&) = delete;

        void release(ptrdiff_t update = 1);
        void acquire();
        bool try_acquire() noexcept;

        template<class Rep, class Period>
        bool try_acquire_for(const std::chrono::duration<Rep, Period>& rel_time);

        template<class Clock, class Duration>
        bool try_acquire_until(const std::chrono::time_point<Clock, Duration>& abs_time);
    };

    using binary_semaphore = counting_semaphore<1>;
}
