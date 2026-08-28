#include <pthread.h>
#include <system_error>
#include <cerrno>
#include <iostream>

void lock_robust_mutex(pthread_mutex_t* mutex) {
    int rc = ::pthread_mutex_lock(mutex);
    if (rc == EOWNERDEAD) {
        std::cerr << "[C++ Відновлення] Попередній процес загинув! Відновлення стану..." << std::endl;
        ::pthread_mutex_consistent(mutex);
    } else if (rc == ENOTRECOVERABLE) {
        throw std::system_error(rc, std::generic_category(), "shared state is unrecoverable");
    } else if (rc != 0) {
        throw std::system_error(rc, std::generic_category(), "pthread_mutex_lock failed");
    }
}
