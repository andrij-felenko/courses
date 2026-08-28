#include <iostream>
#include <memory>
#include <vector>
#include <chrono>
#include <system_error>
#include <span>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <sched.h>
#include <sys/uio.h>
#include <linux/fs.h>   // RWF_HIPRI
#include <liburing.h>

constexpr size_t ALIGNMENT = 4096;
constexpr size_t BLOCK_SIZE = 4096;
constexpr int NUM_ITERATIONS = 100000;

struct AlignedDeleter {
    void operator()(void* p) const { std::free(p); }
};

using AlignedBuffer = std::unique_ptr<uint8_t[], AlignedDeleter>;

AlignedBuffer allocate_aligned_buffer(size_t size, size_t alignment) {
    void* ptr = nullptr;
    if (posix_memalign(&ptr, alignment, size) != 0) {
        throw std::bad_alloc();
    }
    return AlignedBuffer(static_cast<uint8_t*>(ptr));
}

class CpuAffinityGuard {
public:
    explicit CpuAffinityGuard(int cpu_id) {
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(cpu_id, &cpuset);
        if (sched_setaffinity(0, sizeof(cpu_set_t), &cpuset) != 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося прив'язати потік до CPU");
        }
    }
};

class FileDescriptor {
    int fd_{-1};
public:
    explicit FileDescriptor(const char* path, int flags) : fd_(open(path, flags)) {
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка відкриття файла");
        }
    }
    ~FileDescriptor() { if (fd_ >= 0) close(fd_); }
    int get() const noexcept { return fd_; }
};

class IoUringHandle {
    struct io_uring ring_{};
public:
    IoUringHandle(unsigned entries, unsigned flags) {
        if (int ret = io_uring_queue_init(entries, &ring_, flags); ret < 0) {
            throw std::system_error(-ret, std::generic_category(), "Не вдалося ініціалізувати io_uring");
        }
    }
    ~IoUringHandle() { io_uring_queue_exit(&ring_); }
    struct io_uring* get() noexcept { return &ring_; }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " /dev/nvme0n1\n";
        return 1;
    }

    try {
        CpuAffinityGuard affinity(1);
        FileDescriptor fd(argv[1], O_RDONLY | O_DIRECT);
        auto buf = allocate_aligned_buffer(BLOCK_SIZE, ALIGNMENT);

        /* 1. Синхронний polling через preadv2 */
        struct iovec iov{.iov_base = buf.get(), .iov_len = BLOCK_SIZE};
        auto start = std::chrono::high_resolution_clock::now();

        for (int i = 0; i < NUM_ITERATIONS; ++i) {
            off_t offset = (i % 1000) * BLOCK_SIZE;
            ssize_t ret = ::preadv2(fd.get(), &iov, 1, offset, RWF_HIPRI);
            if (ret < 0) {
                throw std::system_error(errno, std::generic_category(), "preadv2 RWF_HIPRI failed");
            }
        }

        auto elapsed = std::chrono::high_resolution_clock::now() - start;
        double total_us = std::chrono::duration<double, std::micro>(elapsed).count();
        std::cout << "preadv2 (RWF_HIPRI): " << (NUM_ITERATIONS / total_us) * 1e6 
                  << " IOPS, середня затримка: " << total_us / NUM_ITERATIONS << " мкс\n";

        /* 2. Асинхронний polling через io_uring */
        IoUringHandle uring(64, IORING_SETUP_IOPOLL);
        start = std::chrono::high_resolution_clock::now();

        for (int i = 0; i < NUM_ITERATIONS; ++i) {
            off_t offset = (i % 1000) * BLOCK_SIZE;
            struct io_uring_sqe* sqe = io_uring_get_sqe(uring.get());
            io_uring_prep_read(sqe, fd.get(), buf.get(), BLOCK_SIZE, offset);

            io_uring_submit(uring.get());

            struct io_uring_cqe* cqe = nullptr;
            int ret = io_uring_wait_cqe(uring.get(), &cqe);
            if (ret < 0 || cqe->res < 0) {
                throw std::runtime_error("Помилка виконання cqe у io_uring");
            }
            io_uring_cqe_seen(uring.get(), cqe);
        }

        elapsed = std::chrono::high_resolution_clock::now() - start;
        total_us = std::chrono::duration<double, std::micro>(elapsed).count();
        std::cout << "io_uring (IOPOLL): " << (NUM_ITERATIONS / total_us) * 1e6 
                  << " IOPS, середня затримка: " << total_us / NUM_ITERATIONS << " мкс\n";

    } catch (const std::exception& ex) {
        std::cerr << "Фатальна помилка: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
