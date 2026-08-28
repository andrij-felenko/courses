// bench_blk_mq.cpp — C++20 ідіоматичний бенчмарк для null_blk
#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <memory>
#include <system_error>
#include <string>
#include <format>
#include <fcntl.h>
#include <unistd.h>

constexpr std::size_t BLOCK_SIZE = 4096;
constexpr std::size_t IO_COUNT = 200000;

// Custom RAII видалятор для вирівняної пам'яті
struct AlignedDeleter {
    void operator()(void* ptr) const noexcept {
        ::free(ptr);
    }
};

using AlignedBuffer = std::unique_ptr<char[], AlignedDeleter>;

AlignedBuffer make_aligned_buffer(std::size_t size, std::size_t alignment) {
    void* ptr = nullptr;
    if (::posix_memalign(&ptr, alignment, size) != 0) {
        throw std::system_error(errno, std::generic_category(), "posix_memalign failed");
    }
    return AlignedBuffer(static_cast<char*>(ptr));
}

// RAII обгортка для файлового дескриптора
class ScopedFd {
    int fd_{-1};
public:
    explicit ScopedFd(const std::string& path, int flags) {
        fd_ = ::open(path.c_str(), flags);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "open failed for " + path);
        }
    }
    ~ScopedFd() {
        if (fd_ >= 0) ::close(fd_);
    }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    [[nodiscard]] int get() const noexcept { return fd_; }
};

void bench_worker(const std::string& dev_path, int thread_id, std::size_t ops) {
    ScopedFd fd(dev_path, O_RDWR | O_DIRECT);
    auto buf = make_aligned_buffer(BLOCK_SIZE, BLOCK_SIZE);
    std::fill_n(buf.get(), BLOCK_SIZE, 0x5A);

    off_t offset = static_cast<off_t>(thread_id) * BLOCK_SIZE * 10000;
    for (std::size_t i = 0; i < ops; ++i) {
        ssize_t ret = ::pwrite(fd.get(), buf.get(), BLOCK_SIZE, offset);
        if (ret != static_cast<ssize_t>(BLOCK_SIZE)) {
            throw std::system_error(errno, std::generic_category(), "pwrite failed");
        }
        offset += BLOCK_SIZE;
    }
}

int main(int argc, char* argv[]) {
    std::string dev = (argc > 1) ? argv[1] : "/dev/nullb0";
    unsigned int num_threads = (argc > 2) ? std::stoul(argv[2]) : std::thread::hardware_concurrency();

    std::cout << std::format("=== C++20 blk-mq бенчмарк на {} (потоків: {}) ===\n", dev, num_threads);

    auto start_time = std::chrono::high_resolution_clock::now();

    std::vector<std::thread> workers;
    workers.reserve(num_threads);

    for (unsigned int i = 0; i < num_threads; ++i) {
        workers.emplace_back(bench_worker, dev, i, IO_COUNT);
    }

    for (auto& worker : workers) {
        if (worker.joinable()) worker.join();
    }

    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end_time - start_time;

    std::size_t total_io = num_threads * IO_COUNT;
    double iops = total_io / elapsed.count();
    double mbps = (iops * BLOCK_SIZE) / (1024.0 * 1024.0);

    std::cout << std::format("Результати:\n");
    std::cout << std::format("  Виконано операцій  : {}\n", total_io);
    std::cout << std::format("  Загальний час     : {:.4f} сек\n", elapsed.count());
    std::cout << std::format("  Продуктивність    : {:.2f} IOPS\n", iops);
    std::cout << std::format("  Пропускна здатність: {:.2f} MB/s\n", mbps);

    return 0;
}
