// bench_sync.cpp — Вимірювання затримок системних викликів скидання кешу в C++20
#include <iostream>
#include <vector>
#include <chrono>
#include <string_view>
#include <memory>
#include <system_error>
#include <span>
#include <cstdint>
#include <unistd.h>
#include <fcntl.h>

namespace storage {

class FileDescriptor {
    int fd_ = -1;

public:
    explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
    ~FileDescriptor() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

class SyncBenchmark {
    static constexpr std::size_t BlockSize = 4096;
    static constexpr std::size_t Iterations = 1000;

    static FileDescriptor open_file(std::string_view path, int flags) {
        int fd = ::open(path.data(), flags, 0644);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити файл");
        }
        return FileDescriptor{fd};
    }

public:
    static void test_fsync(std::string_view path) {
        auto file = open_file(path, O_WRONLY | O_CREAT | O_TRUNC);
        std::vector<std::uint8_t> buffer(BlockSize, 'A');

        auto start = std::chrono::high_resolution_clock::now();
        for (std::size_t i = 0; i < Iterations; ++i) {
            if (::write(file.get(), buffer.data(), buffer.size()) != static_cast<ssize_t>(buffer.size())) {
                throw std::system_error(errno, std::generic_category(), "Запис не вдався");
            }
            if (::fsync(file.get()) < 0) {
                throw std::system_error(errno, std::generic_category(), "fsync не вдався");
            }
        }
        auto elapsed = std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - start).count();
        report("fsync", elapsed);
    }

    static void test_fdatasync(std::string_view path) {
        auto file = open_file(path, O_WRONLY | O_CREAT | O_TRUNC);
        std::vector<std::uint8_t> buffer(BlockSize, 'B');

        auto start = std::chrono::high_resolution_clock::now();
        for (std::size_t i = 0; i < Iterations; ++i) {
            if (::write(file.get(), buffer.data(), buffer.size()) != static_cast<ssize_t>(buffer.size())) {
                throw std::system_error(errno, std::generic_category(), "Запис не вдався");
            }
            if (::fdatasync(file.get()) < 0) {
                throw std::system_error(errno, std::generic_category(), "fdatasync не вдався");
            }
        }
        auto elapsed = std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - start).count();
        report("fdatasync", elapsed);
    }

    static void test_sync_file_range(std::string_view path) {
        auto file = open_file(path, O_WRONLY | O_CREAT | O_TRUNC);
        std::vector<std::uint8_t> buffer(BlockSize, 'C');

        auto start = std::chrono::high_resolution_clock::now();
        off64_t offset = 0;
        for (std::size_t i = 0; i < Iterations; ++i) {
            if (::write(file.get(), buffer.data(), buffer.size()) != static_cast<ssize_t>(buffer.size())) {
                throw std::system_error(errno, std::generic_category(), "Запис не вдався");
            }
            if (::sync_file_range(file.get(), offset, BlockSize,
                                  SYNC_FILE_RANGE_WAIT_BEFORE |
                                  SYNC_FILE_RANGE_WRITE |
                                  SYNC_FILE_RANGE_WAIT_AFTER) < 0) {
                throw std::system_error(errno, std::generic_category(), "sync_file_range не вдався");
            }
            offset += BlockSize;
        }
        auto elapsed = std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - start).count();
        report("sync_file_range", elapsed);
    }

    static void test_odsync(std::string_view path) {
        auto file = open_file(path, O_WRONLY | O_CREAT | O_TRUNC | O_DSYNC);
        std::vector<std::uint8_t> buffer(BlockSize, 'D');

        auto start = std::chrono::high_resolution_clock::now();
        for (std::size_t i = 0; i < Iterations; ++i) {
            if (::write(file.get(), buffer.data(), buffer.size()) != static_cast<ssize_t>(buffer.size())) {
                throw std::system_error(errno, std::generic_category(), "Запис не вдався");
            }
        }
        auto elapsed = std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - start).count();
        report("O_DSYNC", elapsed);
    }

private:
    static void report(std::string_view name, double seconds) {
        double ops = Iterations / seconds;
        double ms_per_op = (seconds / Iterations) * 1000.0;
        std::cout << "  [" << name << "] " << Iterations << " ітерацій: "
                  << seconds << " с (" << ops << " ops/sec, " << ms_per_op << " мс/op)\n";
    }
};

} // namespace storage

int main() {
    std::cout << "=== Бенчмарк скидання кешу (C++20) ===\n";
    constexpr std::string_view testfile = "sync_bench_cpp.tmp";

    try {
        storage::SyncBenchmark::test_fsync(testfile);
        storage::SyncBenchmark::test_fdatasync(testfile);
        storage::SyncBenchmark::test_sync_file_range(testfile);
        storage::SyncBenchmark::test_odsync(testfile);
    } catch (const std::exception& ex) {
        std::cerr << "Помилка тестування: " << ex.what() << '\n';
        ::unlink(testfile.data());
        return 1;
    }

    ::unlink(testfile.data());
    return 0;
}
