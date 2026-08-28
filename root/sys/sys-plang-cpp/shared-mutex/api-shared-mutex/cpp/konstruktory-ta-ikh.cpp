namespace std {
    template <class Mutex>
    class shared_lock {
    public:
        using mutex_type = Mutex;

        // 1. Порожній конструктор
        shared_lock() noexcept : pm(nullptr), owns(false) {}

        // 2. Стандартне сумісне блокування (захоплює lock_shared)
        explicit shared_lock(mutex_type& m) 
            : pm(std::addressof(m)), owns(true) { m.lock_shared(); }

        // 3. Відкладене блокування (без виклику lock_shared)
        shared_lock(mutex_type& m, defer_lock_t) noexcept 
            : pm(std::addressof(m)), owns(false) {}

        // 4. Спроба блокування без зупинки потоку
        shared_lock(mutex_type& m, try_to_lock_t) 
            : pm(std::addressof(m)), owns(m.try_lock_shared()) {}

        // 5. Перебрання вже захопленого замка
        shared_lock(mutex_type& m, adopt_lock_t) 
            : pm(std::addressof(m)), owns(true) {}

        // 6. Конструктори з часовими інтервалами
        template <class Rep, class Period>
        shared_lock(mutex_type& m, const chrono::duration<Rep, Period>& timeout_duration)
            : pm(std::addressof(m)), owns(m.try_lock_shared_for(timeout_duration)) {}

        template <class Clock, class Duration>
        shared_lock(mutex_type& m, const chrono::time_point<Clock, Duration>& timeout_time)
            : pm(std::addressof(m)), owns(m.try_lock_shared_until(timeout_time)) {}

        // Деструктор
        ~shared_lock() {
            if (owns) pm->unlock_shared();
        }

        // Оператори переміщення
        shared_lock(shared_lock&& u) noexcept 
            : pm(u.pm), owns(u.owns) { u.pm = nullptr; u.owns = false; }

        shared_lock& operator=(shared_lock&& u) noexcept {
            if (owns) pm->unlock_shared();
            pm = u.pm; owns = u.owns;
            u.pm = nullptr; u.owns = false;
            return *this;
        }

        // Заборона копіювання
        shared_lock(const shared_lock&) = delete;
        shared_lock& operator=(const shared_lock&) = delete;
    };
}
