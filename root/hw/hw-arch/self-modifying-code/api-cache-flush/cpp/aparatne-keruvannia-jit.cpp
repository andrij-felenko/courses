#include <pthread.h>

// RAII обгортка для тимчасового відкриття прав на запис у потік JIT
class ScopedJitWriteAccess {
public:
    ScopedJitWriteAccess() noexcept {
        pthread_jit_write_protect_np(0); // Дозволити запис у поточному потоці
    }
    ~ScopedJitWriteAccess() noexcept {
        pthread_jit_write_protect_np(1); // Повернути режим виконання
    }
    ScopedJitWriteAccess(const ScopedJitWriteAccess&) = delete;
    ScopedJitWriteAccess& operator=(const ScopedJitWriteAccess&) = delete;
};
