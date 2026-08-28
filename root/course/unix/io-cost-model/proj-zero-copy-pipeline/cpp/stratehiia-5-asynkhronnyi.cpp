#include <liburing.h>
#include <unistd.h>
#include <vector>
#include <memory>
#include <cstdlib>
#include <system_error>

class UringHandle {
public:
    explicit UringHandle(unsigned entries, unsigned flags = 0) {
        if (::io_uring_queue_init(entries, &ring_, flags) < 0) {
            throw std::system_error(errno, std::generic_category(), "io_uring_queue_init failed");
        }
    }
    ~UringHandle() noexcept {
        ::io_uring_queue_exit(&ring_);
    }
    UringHandle(const UringHandle&) = delete;
    UringHandle& operator=(const UringHandle&) = delete;

    [[nodiscard]] struct io_uring* get() noexcept { return &ring_; }

private:
    struct io_uring ring_{};
};

constexpr unsigned QueueDepth = 64;
constexpr std::size_t UringChunkSize = 64 * 1024;

ssize_t run_io_uring_pipeline_cpp(int fd_in, int fd_out, std::size_t total_bytes) {
    UringHandle ring(QueueDepth);

    void* raw_buf = nullptr;
    if (::posix_memalign(&raw_buf, 4096, QueueDepth * UringChunkSize) != 0) {
        return -1;
    }
    auto buffer_deleter = [](void* p) { std::free(p); };
    std::unique_ptr<void, decltype(buffer_deleter)> buf_holder(raw_buf, buffer_deleter);
    auto* buffers = static_cast<char*>(raw_buf);

    std::vector<struct iovec> iov(QueueDepth);
    for (unsigned i = 0; i < QueueDepth; ++i) {
        iov[i].iov_base = buffers + (i * UringChunkSize);
        iov[i].iov_len = UringChunkSize;
    }

    ::io_uring_register_buffers(ring.get(), iov.data(), QueueDepth);

    std::size_t bytes_transferred = 0;
    off_t in_offset = 0;
    off_t out_offset = 0;

    while (bytes_transferred < total_bytes) {
        int submitted = 0;

        for (unsigned i = 0; i < QueueDepth && bytes_transferred + (submitted * UringChunkSize) < total_bytes; ++i) {
            struct io_uring_sqe* sqe = ::io_uring_get_sqe(ring.get());
            if (!sqe) break;

            ::io_uring_prep_read_fixed(sqe, fd_in, iov[i].iov_base, UringChunkSize, in_offset, static_cast<int>(i));
            sqe->user_data = i;
            in_offset += static_cast<off_t>(UringChunkSize);
            submitted++;
        }

        if (submitted == 0) break;

        ::io_uring_submit_and_wait(ring.get(), static_cast<unsigned>(submitted));

        for (int i = 0; i < submitted; ++i) {
            struct io_uring_cqe* cqe = nullptr;
            if (::io_uring_peek_cqe(ring.get(), &cqe) == 0) {
                if (cqe->res > 0) {
                    auto buf_idx = static_cast<unsigned>(cqe->user_data);
                    struct io_uring_sqe* sqe_w = ::io_uring_get_sqe(ring.get());
                    if (sqe_w) {
                        ::io_uring_prep_write_fixed(sqe_w, fd_out, iov[buf_idx].iov_base,
                                                   static_cast<unsigned>(cqe->res), out_offset, static_cast<int>(buf_idx));
                        sqe_w->user_data = buf_idx;
                        out_offset += cqe->res;
                        bytes_transferred += static_cast<std::size_t>(cqe->res);
                    }
                }
                ::io_uring_cqe_seen(ring.get(), cqe);
            }
        }

        ::io_uring_submit_and_wait(ring.get(), 1);
        struct io_uring_cqe* cqe_w = nullptr;
        while (::io_uring_peek_cqe(ring.get(), &cqe_w) == 0) {
            ::io_uring_cqe_seen(ring.get(), cqe_w);
        }
    }

    ::io_uring_unregister_buffers(ring.get());
    return static_cast<ssize_t>(bytes_transferred);
}
