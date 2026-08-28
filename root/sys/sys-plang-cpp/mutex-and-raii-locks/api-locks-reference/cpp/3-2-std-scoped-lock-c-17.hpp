namespace std {
    template <class... MutexTypes>
    class scoped_lock {
    public:
        using mutex_type = /* лише якщо sizeof...(MutexTypes) == 1 */;

        explicit scoped_lock(MutexTypes&... m);
        scoped_lock(adopt_lock_t t, MutexTypes&... m);
        explicit scoped_lock(MutexTypes& m);
        scoped_lock() noexcept; // порожній замок для 0 м'ютексів
        ~scoped_lock();

        scoped_lock(const scoped_lock&) = delete;
        scoped_lock& operator=(const scoped_lock&) = delete;
    };
}
