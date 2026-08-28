namespace std {
    template <class Mutex>
    class shared_lock {
    public:
        using mutex_type = Mutex;

        shared_lock() noexcept;
        explicit shared_lock(mutex_type& m); // викликає m.lock_shared()
        shared_lock(mutex_type& m, defer_lock_t) noexcept;
        shared_lock(mutex_type& m, try_to_lock_t);
        shared_lock(mutex_type& m, adopt_lock_t);
        ~shared_lock();                      // викликає m.unlock_shared()

        shared_lock(const shared_lock&) = delete;
        shared_lock& operator=(const shared_lock&) = delete;

        shared_lock(shared_lock&& u) noexcept;
        shared_lock& operator=(shared_lock&& u) noexcept;

        void lock();
        bool try_lock();
        void unlock();

        bool owns_lock() const noexcept;
        explicit operator bool() const noexcept;
    };
}
