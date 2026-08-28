#include <iostream>
#include <pthread.h>
#include <shared_mutex>

// У стандартному C++ std::shared_mutex використовує системну політику за замовчуванням.
// Для явного задання пріоритету письменників створюється RAII-обгортка над POSIX-атрибутами.
class NativeConfiguredRwLock {
public:
    NativeConfiguredRwLock() {
        pthread_rwlockattr_t attr;
        pthread_rwlockattr_init(&attr);
        pthread_rwlockattr_setkind_np(&attr, PTHREAD_RWLOCK_PREFER_WRITER_NONRECURSIVE_NP);
        pthread_rwlock_init(&rwlock_, &attr);
        pthread_rwlockattr_destroy(&attr);
    }

    ~NativeConfiguredRwLock() {
        pthread_rwlock_destroy(&rwlock_);
    }

    void lock_shared() { pthread_rwlock_rdlock(&rwlock_); }
    void unlock_shared() { pthread_rwlock_unlock(&rwlock_); }
    void lock() { pthread_rwlock_wrlock(&rwlock_); }
    void unlock() { pthread_rwlock_unlock(&rwlock_); }

    NativeConfiguredRwLock(const NativeConfiguredRwLock&) = delete;
    NativeConfiguredRwLock& operator=(const NativeConfiguredRwLock&) = delete;

private:
    pthread_rwlock_t rwlock_;
};
