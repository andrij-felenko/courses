// fstrim_example.cpp — Ідіоматичний виклик FITRIM у C++17
#include <iostream>
#include <filesystem>
#include <system_error>
#include <string_view>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/fs.h>

class FileDescriptor {
public:
    explicit FileDescriptor(const std::filesystem::path& path) {
        fd_ = ::open(path.c_str(), O_RDONLY | O_DIRECTORY);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити каталог");
        }
    }

    ~FileDescriptor() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    [[nodiscard]] int get() const noexcept { return fd_; }

private:
    int fd_{-1};
};

uint64_t execute_fstrim(const std::filesystem::path& mount_point, uint64_t minlen_bytes = 1048576) {
    FileDescriptor fd(mount_point);

    fstrim_range range{};
    range.start = 0;
    range.len = static_cast<uint64_t>(-1);
    range.minlen = minlen_bytes;

    if (::ioctl(fd.get(), FITRIM, &range) < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка виконання ioctl(FITRIM)");
    }

    return range.len;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <точка_монтування>\n";
        return EXIT_FAILURE;
    }

    try {
        std::filesystem::path mount_point = argv[1];
        std::cout << "Виконання TRIM для: " << mount_point << "...\n";
        
        uint64_t trimmed_bytes = execute_fstrim(mount_point);
        
        std::cout << "Успішно! FTL підтвердив очищення: " << trimmed_bytes << " байтів ("
                  << static_cast<double>(trimmed_bytes) / (1024.0 * 1024.0) << " МБ)\n";
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
