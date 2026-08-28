#include <liburing.h>
#include <stdexcept>

class IoUringAsyncPoller {
    struct io_uring ring_{};
public:
    explicit IoUringAsyncPoller(unsigned entries) {
        if (int ret = io_uring_queue_init(entries, &ring_, IORING_SETUP_IOPOLL); ret < 0) {
            throw std::runtime_error("Не вдалося ініціалізувати io_uring IOPOLL");
        }
    }
    ~IoUringAsyncPoller() { io_uring_queue_exit(&ring_); }
    struct io_uring* get() noexcept { return &ring_; }
};
