#include <pthread.h>
#include <system_error>
#include <cerrno>

class RobustProcessMutex {
    pthread_mutex_t* mutex_{nullptr};
public:
    explicit RobustProcessMutex(pthread_mutex_t* m) noexcept : mutex_(m) {}

    void lock_and_repair(auto&& repair_fn) {
        int rc = pthread_mutex_lock(mutex_);
        if (rc == EOWNERDEAD) {
            // Попередній процес аварійно загинув
            repair_fn();
            pthread_mutex_consistent(mutex_);
        } else if (rc != 0) {
            throw std::system_error(rc, std::generic_category(), "pthread_mutex_lock failed");
        }
    }

    void unlock() noexcept {
        pthread_mutex_unlock(mutex_);
    }
};
