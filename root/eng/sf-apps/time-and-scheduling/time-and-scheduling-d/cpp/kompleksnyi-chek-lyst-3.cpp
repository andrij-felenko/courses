// RAII блокування сторінок процесу в оперативній пам'яті
struct MemoryLock {
    MemoryLock() {
        if (::mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
            throw std::system_error(errno, std::generic_category(), "mlockall failed");
        }
    }
    ~MemoryLock() {
        ::munlockall();
    }
};
