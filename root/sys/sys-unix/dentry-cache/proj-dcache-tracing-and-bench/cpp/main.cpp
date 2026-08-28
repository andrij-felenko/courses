#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <filesystem>
#include <vector>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

class ScopedDir {
public:
    explicit ScopedDir(const fs::path& p) : path_(p) {
        fs::create_directories(path_);
    }
    ~ScopedDir() {
        std::error_code ec;
        fs::remove_all(path_, ec);
    }
    const fs::path& path() const noexcept { return path_; }

private:
    fs::path path_;
};

class DcacheBenchmark {
public:
    static constexpr int Iterations = 1'000'000;

    static double Measure(int dirfd, std::string_view filename) {
        struct stat st;
        const auto start = std::chrono::steady_clock::now();

        for (int i = 0; i < Iterations; ++i) {
            fstatat(dirfd, filename.data(), &st, AT_SYMLINK_NOFOLLOW);
        }

        const auto end = std::chrono::steady_clock::now();
        const std::chrono::duration<double, std::nano> elapsed = end - start;
        return elapsed.count() / Iterations;
    }
};

int main() {
    const fs::path bench_dir = "/tmp/dcache_bench_cpp";
    ScopedDir guard(bench_dir);

    const std::string existing_file = "present_file.txt";
    const std::string missing_file = "absent_file.txt";

    int dirfd = open(bench_dir.c_str(), O_RDONLY | O_DIRECTORY);
    if (dirfd < 0) {
        std::cerr << "Не вдалося відкрити тестовий каталог\n";
        return 1;
    }

    // Створюємо існуючий файл
    int fd = openat(dirfd, existing_file.c_str(), O_CREAT | O_WRONLY | O_TRUNC, 0644);
    if (fd >= 0) close(fd);

    std::cout << "=== Бенчмарк швидкодії dcache (C++20, ітерацій: "
              << DcacheBenchmark::Iterations << ") ===\n";

    // 1. Позитивний хіт
    const double pos_time = DcacheBenchmark::Measure(dirfd, existing_file);
    std::cout << "1. Positive dentry hit (існуючий файл):       "
              << pos_time << " нс / виклик\n";

    // Прогріваємо негативний dentry
    struct stat dummy;
    fstatat(dirfd, missing_file.c_str(), &dummy, AT_SYMLINK_NOFOLLOW);

    // 2. Негативний хіт
    const double neg_time = DcacheBenchmark::Measure(dirfd, missing_file);
    std::cout << "2. Negative dentry hit (відсутній, кешований): "
              << neg_time << " нс / виклик\n";

    close(dirfd);
    return 0;
}
