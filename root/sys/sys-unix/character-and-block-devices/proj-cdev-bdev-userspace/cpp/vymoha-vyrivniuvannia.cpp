#define _GNU_SOURCE
#include <iostream>
#include <memory>
#include <span>
#include <system_error>
#include <cstdlib>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/fs.h>

// Кастомний видаляч для std::unique_ptr, який викликає free() для вирівняної пам'яті
struct AlignedDeleter {
    void operator()(void* ptr) const noexcept {
        ::free(ptr);
    }
};

class BlockDeviceDirectReader {
    int fd_{-1};
    uint64_t total_size_{0};
    int sector_size_{0};

public:
    explicit BlockDeviceDirectReader(const char* dev_path) {
        fd_ = ::open(dev_path, O_RDONLY | O_DIRECT);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Не вдалося відкрити bdev у режимі O_DIRECT");
        }

        if (::ioctl(fd_, BLKGETSIZE64, &total_size_) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), 
                                   "Помилка опитування ioctl(BLKGETSIZE64)");
        }

        if (::ioctl(fd_, BLKSSZGET, &sector_size_) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), 
                                   "Помилка опитування ioctl(BLKSSZGET)");
        }
    }

    ~BlockDeviceDirectReader() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    [[nodiscard]] uint64_t size() const noexcept { return total_size_; }
    [[nodiscard]] int sector_size() const noexcept { return sector_size_; }

    void read_aligned_sectors(uint64_t start_sector, size_t sector_count) {
        size_t bytes_to_read = static_cast<size_t>(sector_size_) * sector_count;
        void* raw_ptr = nullptr;

        // Безпечне виділення пам'яті з гарантованим вирівнюванням
        if (::posix_memalign(&raw_ptr, sector_size_, bytes_to_read) != 0) {
            throw std::bad_alloc();
        }

        // Автоматичне управління життєвим циклом буфера через RAII
        std::unique_ptr<void, AlignedDeleter> aligned_buffer(raw_ptr);

        off_t offset = static_cast<off_t>(start_sector * sector_size_);
        if (::lseek(fd_, offset, SEEK_SET) < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Помилка позиціонування lseek");
        }

        ssize_t bytes_read = ::read(fd_, aligned_buffer.get(), bytes_to_read);
        if (bytes_read < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Помилка прямого читання Direct I/O");
        }

        std::cout << "C++ RAII Direct I/O: успішно прочитано " << bytes_read 
                  << " байтів починаючи з сектора " << start_sector << "\n";
    }
};

int main(int argc, char* argv[]) {
    const char* target_dev = (argc > 1) ? argv[1] : "/dev/loop0";
    try {
        BlockDeviceDirectReader bdev(target_dev);
        std::cout << "Пристрій: " << target_dev << "\n";
        std::cout << "Розмір: " << bdev.size() << " байтів, Сектор: " 
                  << bdev.sector_size() << " байтів\n";

        // Прочитати 2 вирівняні сектори з початку накопичувача
        bdev.read_aligned_sectors(0, 2);
    } catch (const std::exception& ex) {
        std::cerr << "Критичний виняток Bdev: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
