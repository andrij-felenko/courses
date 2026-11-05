#include <pthread.h>
#include <stdexcept>

// C++ RAII-обгортка для гарантування суворого контракту утримання спін-замка
class PosixSpinlockGuard {
private:
    pthread_spinlock_t& spinlock_;

public:
    // Конструктор захоплює замок при вході у блок коду
    explicit PosixSpinlockGuard(pthread_spinlock_t& spinlock) : spinlock_(spinlock) {
        if (pthread_spin_lock(&spinlock_) != 0) {
            throw std::runtime_error("Не вдалося захопити спін-замок");
        }
    }

    // Деструктор автоматично звільняє замок при виході з блоку (навіть при винятках)
    ~PosixSpinlockGuard() noexcept {
        pthread_spin_unlock(&spinlock_);
    }

    // Забороняємо переміщення та копіювання для запобігання помилкам володіння
    PosixSpinlockGuard(const PosixSpinlockGuard&) = delete;
    PosixSpinlockGuard& operator=(const PosixSpinlockGuard&) = delete;
};

// Приклад використання RAII-обгортки у C++
class CounterService {
private:
    pthread_spinlock_t lock_;
    long counter_{0};

public:
    CounterService() {
        pthread_spin_init(&lock_, PTHREAD_PROCESS_PRIVATE);
    }

    ~CounterService() {
        pthread_spin_destroy(&lock_);
    }

    void increment() {
        // Захоплення та автоматичне звільнення замка через RAII-контекст
        PosixSpinlockGuard guard(lock_);
        // Лише надкоротка атомарна або неблокуюча модифікація стану
        counter_++;
    }
};
