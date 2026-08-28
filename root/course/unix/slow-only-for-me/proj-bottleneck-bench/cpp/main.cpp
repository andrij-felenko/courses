#include <iostream>
#include <vector>
#include <string_view>
#include <thread>
#include <mutex>
#include <chrono>
#include <span>
#include <memory>
#include <fcntl.h>
#include <unistd.h>
#include <system_error>
#include <cstring>

namespace {

constexpr size_t THREAD_COUNT = 8;
constexpr size_t SYSCALL_ITERATIONS = 2'000'000;
constexpr size_t IO_ITERATIONS = 2'000;

class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(const char* path, int flags, mode_t mode = 0644) {
        fd_ = ::open(path, flags, mode);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка відкриття дескриптора");
        }
    }
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }
    
    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;
    UniqueFd(UniqueFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
};

void run_cpu_bound() {
    std::cout << "[CPU-bound] Старт обчислень. PID: " << ::getpid() << '\n';
    volatile uint64_t hash = 0x123456789ABCDEF0ULL;
    while (true) {
        for (uint64_t i = 0; i < 100'000'000ULL; ++i) {
            hash ^= (i + 0x9e3779b9 + (hash << 6) + (hash >> 2));
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
}

void run_syscall_bound() {
    std::cout << "[Kernel-bound] Старт шторму системних викликів. PID: " << ::getpid() << '\n';
    UniqueFd null_dev("/dev/null", O_WRONLY);
    const char byte = 'A';
    while (true) {
        for (size_t i = 0; i < SYSCALL_ITERATIONS; ++i) {
            if (::write(null_dev.get(), &byte, 1) != 1) {
                throw std::system_error(errno, std::generic_category(), "Помилка запису у /dev/null");
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
}

void run_lock_contention() {
    std::cout << "[Lock-bound] Старт потоків із м'ютексом. PID: " << ::getpid() << '\n';
    std::mutex mtx;
    volatile uint64_t counter = 0;
    std::vector<std::jthread> workers;
    workers.reserve(THREAD_COUNT);

    for (size_t i = 0; i < THREAD_COUNT; ++i) {
        workers.emplace_back([&mtx, &counter]() {
            while (true) {
                for (size_t k = 0; k < 100'000; ++k) {
                    std::lock_guard<std::mutex> lock(mtx);
                    counter++;
                }
                std::this_thread::sleep_for(std::chrono::milliseconds(1));
            }
        });
    }
}

void run_io_bound() {
    const char* path = "/tmp/bottleneck_sync_cpp.tmp";
    std::cout << "[I/O-bound] Старт синхронного введення-виведення. PID: " << ::getpid() << '\n';
    UniqueFd sync_file(path, O_WRONLY | O_CREAT | O_TRUNC | O_SYNC, 0644);

    std::vector<char> buffer(4096, 'Z');
    while (true) {
        for (size_t i = 0; i < IO_ITERATIONS; ++i) {
            if (::write(sync_file.get(), buffer.data(), buffer.size()) != static_cast<ssize_t>(buffer.size())) {
                throw std::system_error(errno, std::generic_category(), "Помилка sync write");
            }
            ::fdatasync(sync_file.get());
        }
        ::lseek(sync_file.get(), 0, SEEK_SET);
    }
}

} // namespace

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " [cpu|syscall|lock|io]\n";
        return 1;
    }

    const std::string_view mode = argv[1];
    try {
        if (mode == "cpu") run_cpu_bound();
        else if (mode == "syscall") run_syscall_bound();
        else if (mode == "lock") run_lock_contention();
        else if (mode == "io") run_io_bound();
        else {
            std::cerr << "Невідомий режим: " << mode << '\n';
            return 1;
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
