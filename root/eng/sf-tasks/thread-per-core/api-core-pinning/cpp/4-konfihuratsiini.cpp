#include <liburing.h>
#include <system_error>
#include <cstring>

namespace tpc {

/* RAII обгортка над екземпляром io_uring для потоку ядра */
class ScopedIoUring {
public:
    ScopedIoUring(unsigned entries, int cpu_affinity) {
        io_uring_params params{};
        params.flags = IORING_SETUP_SQPOLL | IORING_SETUP_SQ_AFFINITY;
        params.sq_thread_cpu = static_cast<uint32_t>(cpu_affinity);
        params.sq_thread_idle = 2000; // 2 секунди очікування ядра

        const int rc = io_uring_queue_init_params(entries, &ring_, &params);
        if (rc < 0) {
            throw std::system_error(-rc, std::generic_category(), "Помилка ініціалізації io_uring");
        }
    }

    ~ScopedIoUring() noexcept {
        io_uring_queue_exit(&ring_);
    }

    ScopedIoUring(const ScopedIoUring&) = delete;
    ScopedIoUring& operator=(const ScopedIoUring&) = delete;

    struct io_uring* get() noexcept { return &ring_; }

private:
    struct io_uring ring_{};
};

} // namespace tpc
