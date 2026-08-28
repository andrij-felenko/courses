// f2fs_ops.cpp — RAII-обгортка та ідіоматичне керування F2FS ioctl у C++20.
// Збірка: g++ -std=c++20 -O2 -o f2fs_ops_cpp f2fs_ops.cpp
#include <iostream>
#include <string_view>
#include <system_error>
#include <utility>
#include <cstdint>
#include <cerrno>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/f2fs_fs.h>

namespace f2fs {

// RAII обгортка для безпечного керування файловим дескриптором F2FS
class FileDescriptor {
    int fd_{-1};
public:
    explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
    ~FileDescriptor() {
        if (fd_ >= 0) ::close(fd_);
    }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(std::exchange(other.fd_, -1)) {}
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = std::exchange(other.fd_, -1);
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

// RAII транзакція атомарного запису в F2FS
class AtomicTransaction {
    int fd_{-1};
    bool committed_{false};
public:
    explicit AtomicTransaction(int fd) : fd_(fd) {
        if (::ioctl(fd_, F2FS_IOC_START_ATOMIC_WRITE) < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "F2FS_IOC_START_ATOMIC_WRITE failed");
        }
    }

    ~AtomicTransaction() {
        if (fd_ >= 0 && !committed_) {
            // Скасувати транзакцію в деструкторі при винятку або помилці
            ::ioctl(fd_, F2FS_IOC_ABORT_ATOMIC_WRITE);
        }
    }

    void commit() {
        if (committed_) return;
        if (::ioctl(fd_, F2FS_IOC_COMMIT_ATOMIC_WRITE) < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "F2FS_IOC_COMMIT_ATOMIC_WRITE failed");
        }
        committed_ = true;
    }

    AtomicTransaction(const AtomicTransaction&) = delete;
    AtomicTransaction& operator=(const AtomicTransaction&) = delete;
};

// Допоміжні функції керування F2FS
[[nodiscard]] bool get_pin_status(int fd) {
    uint32_t pin = 0;
    if (::ioctl(fd, F2FS_IOC_GET_PIN_FILE, &pin) < 0) {
        throw std::system_error(errno, std::generic_category(), 
                               "F2FS_IOC_GET_PIN_FILE failed");
    }
    return pin != 0;
}

void trigger_garbage_collection(int fd, bool sync) {
    uint32_t sync_val = sync ? 1 : 0;
    if (::ioctl(fd, F2FS_IOC_GARBAGE_COLLECT, &sync_val) < 0) {
        throw std::system_error(errno, std::generic_category(), 
                               "F2FS_IOC_GARBAGE_COLLECT failed");
    }
}

} // namespace f2fs

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_файла>\n";
        return 1;
    }

    try {
        int raw_fd = ::open(argv[1], O_RDWR | O_CREAT, 0644);
        if (raw_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "open failed");
        }
        f2fs::FileDescriptor file{raw_fd};

        bool is_pinned = f2fs::get_pin_status(file.get());
        std::cout << "Стан прикріплення: " << (is_pinned ? "pinned" : "unpinned") << '\n';

        // Виконання безпечної RAII транзакції
        {
            f2fs::AtomicTransaction tx{file.get()};
            std::string_view payload = "CPP20_ATOMIC_TRANSACTION_PAYLOAD";
            ssize_t res = ::write(file.get(), payload.data(), payload.size());
            if (res < 0 || static_cast<size_t>(res) != payload.size()) {
                throw std::system_error(errno, std::generic_category(), "write failed");
            }
            tx.commit();
            std::cout << "Атомарний запис зафіксовано в C++!\n";
        }

    } catch (const std::exception& ex) {
        std::cerr << "Помилка F2FS: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
