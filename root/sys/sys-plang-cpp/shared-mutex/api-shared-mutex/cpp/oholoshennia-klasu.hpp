namespace std {
    class shared_mutex {
    public:
        shared_mutex();
        ~shared_mutex();

        shared_mutex(const shared_mutex&) = delete;
        shared_mutex& operator=(const shared_mutex&) = delete;

        // Монопольний режим (Exclusive Access / Writer)
        void lock();
        bool try_lock();
        void unlock();

        // Сумісний режим (Shared Access / Reader)
        void lock_shared();
        bool try_lock_shared();
        void unlock_shared();

        // Отримання системного дескриптора (опційно у деяких реалізаціях)
        using native_handle_type = /* системно-залежний тип */;
        native_handle_type native_handle();
    };
}
