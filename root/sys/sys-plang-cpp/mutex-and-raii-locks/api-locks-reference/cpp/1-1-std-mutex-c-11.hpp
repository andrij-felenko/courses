namespace std {
    class mutex {
    public:
        constexpr mutex() noexcept;
        ~mutex();

        mutex(const mutex&) = delete;
        mutex& operator=(const mutex&) = delete;

        void lock();
        bool try_lock();
        void unlock();

        using native_handle_type = /* implementation-defined */;
        native_handle_type native_handle();
    };
}
