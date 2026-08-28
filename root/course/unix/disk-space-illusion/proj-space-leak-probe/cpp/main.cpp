#include <iostream>
#include <filesystem>
#include <fstream>
#include <vector>
#include <string>
#include <system_error>
#include <memory>
#include <span>
#include <cstdint>
#include <unistd.h>
#include <fcntl.h>
#include <sys/statvfs.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

class FileDescriptor {
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

private:
    int fd_{-1};
};

struct VfsMetrics {
    std::uint64_t total_kib{0};
    std::uint64_t free_kib{0};
    std::uint64_t avail_kib{0};
    std::uint64_t du_kib{0};
};

class DiskInspector {
public:
    static std::uint64_t calculate_directory_usage(const fs::path& root_path) {
        std::uint64_t total_bytes = 0;
        std::error_code ec;
        if (!fs::exists(root_path, ec)) return 0;

        for (const auto& entry : fs::recursive_directory_iterator(root_path, fs::directory_options::skip_permission_denied, ec)) {
            if (entry.is_regular_file(ec)) {
                struct stat st{};
                if (::lstat(entry.path().c_str(), &st) == 0) {
                    total_bytes += static_cast<std::uint64_t>(st.st_blocks) * 512;
                }
            }
        }
        return total_bytes;
    }

    static VfsMetrics inspect(const fs::path& target_path) {
        struct statvfs st{};
        if (::statvfs(target_path.c_str(), &st) != 0) {
            throw std::system_error(errno, std::generic_category(), "statvfs failed");
        }

        const auto block_size = static_cast<std::uint64_t>(st.f_frsize);
        VfsMetrics metrics;
        metrics.total_kib = (st.f_blocks * block_size) / 1024;
        metrics.free_kib = (st.f_bfree * block_size) / 1024;
        metrics.avail_kib = (st.f_bavail * block_size) / 1024;
        metrics.du_kib = calculate_directory_usage(target_path) / 1024;
        return metrics;
    }

    static void print_status(const fs::path& target_path, std::string_view phase_label) {
        const auto m = inspect(target_path);
        std::cout << "\n[" << phase_label << "]\n"
                  << "  Точка VFS:          " << target_path << "\n"
                  << "  Загалом (VFS):      " << m.total_kib << " KiB (" << m.total_kib / 1024 << " MiB)\n"
                  << "  Вільно (f_bfree):   " << m.free_kib << " KiB (" << m.free_kib / 1024 << " MiB)\n"
                  << "  Доступно (f_bavail): " << m.avail_kib << " KiB (" << m.avail_kib / 1024 << " MiB)\n"
                  << "  Каталог (du/stat):  " << m.du_kib << " KiB (" << m.du_kib / 1024 << " MiB)\n";
    }
};

int main() {
    const fs::path test_dir = "/tmp/disk_test_cpp_leak";
    const fs::path test_file = test_dir / "phantom_cpp.bin";
    constexpr std::size_t alloc_bytes = 64 * 1024 * 1024; // 64 MiB

    std::error_code ec;
    fs::create_directories(test_dir, ec);

    DiskInspector::print_status(test_dir, "ЕТАП 1: Чистий каталог");

    FileDescriptor fd(::open(test_file.c_str(), O_CREAT | O_RDWR | O_TRUNC, 0644));
    if (!fd.valid()) {
        std::cerr << "Помилка відкриття файлу: " << std::generic_category().message(errno) << "\n";
        return 1;
    }

    if (::posix_fallocate(fd.get(), 0, alloc_bytes) != 0) {
        std::vector<char> buffer(4096, '\xBB');
        for (std::size_t i = 0; i < alloc_bytes / buffer.size(); ++i) {
            if (::write(fd.get(), buffer.data(), buffer.size()) != static_cast<ssize_t>(buffer.size())) {
                std::cerr << "Write error\n";
                return 1;
            }
        }
    }
    ::fsync(fd.get());

    DiskInspector::print_status(test_dir, "ЕТАП 2: Файл 64 MiB створено й зафіксовано на диску");

    if (::unlink(test_file.c_str()) != 0) {
        std::cerr << "Unlink error: " << std::generic_category().message(errno) << "\n";
        return 1;
    }

    DiskInspector::print_status(test_dir, "ЕТАП 3: Файл видалено з каталогу (unlink), але дескриптор відкрито");

    const fs::path proc_fd = fs::path("/proc/self/fd") / std::to_string(fd.get());
    if (fs::exists(proc_fd, ec)) {
        const auto target = fs::read_symlink(proc_fd, ec);
        std::cout << "\n--> Інспекція /proc/self/fd:\n"
                  << "  Дескриптор " << proc_fd << " посилається на: " << target << "\n";
    }

    std::cout << "\n--> Вивільнення блоків на льоту через ::ftruncate(fd, 0)...\n";
    if (::ftruncate(fd.get(), 0) != 0) {
        std::cerr << "ftruncate failed: " << std::generic_category().message(errno) << "\n";
    }

    DiskInspector::print_status(test_dir, "ЕТАП 4: Розмір скинуто до 0 (блоки звільнено)");

    fs::remove_all(test_dir, ec);
    std::cout << "\nТестування успішно завершено.\n";
    return 0;
}
