namespace std {
    class shared_mutex {
    public:
        shared_mutex();
        ~shared_mutex();

        shared_mutex(const shared_mutex&) = delete;
        shared_mutex& operator=(const shared_mutex&) = delete;

        // Ексклюзивне володіння (Writers)
        void lock();
        bool try_lock();
        void unlock();

        // Спільне володіння (Readers)
        void lock_shared();
        bool try_lock_shared();
        void unlock_shared();
    };
}
