struct MutexLockGuard {
    explicit MutexLockGuard(std::mutex& mtx) : m_mtx(mtx) { m_mtx.lock(); }
    ~MutexLockGuard() { m_mtx.unlock(); }

    MutexLockGuard(const MutexLockGuard&) = delete;
    MutexLockGuard(MutexLockGuard&&) = delete;

private:
    std::mutex& m_mtx;
};

MutexLockGuard create_guard(std::mutex& mtx) {
    return MutexLockGuard(mtx); // Повністю легально в C++17! У C++14 — помилка компіляції.
}

std::mutex g_mtx;
MutexLockGuard lock = create_guard(g_mtx); // Пряме створення замка за місцем
