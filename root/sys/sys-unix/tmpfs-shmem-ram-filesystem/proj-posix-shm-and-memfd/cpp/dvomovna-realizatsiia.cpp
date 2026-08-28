#include <iostream>
#include <string_view>
#include <span>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>

// Ідіоматична обгортка RAII для анонімної пам'яті memfd у C++
class SealedMemFd {
public:
    SealedMemFd(int fd, std::size_t size) noexcept : fd_{fd}, size_{size} {}
    
    ~SealedMemFd() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SealedMemFd(const SealedMemFd&) = delete;
    SealedMemFd& operator=(const SealedMemFd&) = delete;

    SealedMemFd(SealedMemFd&& other) noexcept : fd_{other.fd_}, size_{other.size_} {
        other.fd_ = -1;
        other.size_ = 0;
    }

    SealedMemFd& operator=(SealedMemFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            size_ = other.size_;
            other.fd_ = -1;
            other.size_ = 0;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }
    [[nodiscard]] std::size_t size() const noexcept { return size_; }

    static std::expected<SealedMemFd, std::error_code> create(
        std::string_view name,
        std::size_t size,
        std::span<const std::uint8_t> initial_data = {}
    ) {
        int fd = ::memfd_create(name.data(), MFD_ALLOW_SEALING | MFD_CLOEXEC);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::ftruncate(fd, static_cast<off_t>(size)) < 0) {
            int err = errno;
            ::close(fd);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        if (!initial_data.empty()) {
            void* ptr = ::mmap(nullptr, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
            if (ptr == MAP_FAILED) {
                int err = errno;
                ::close(fd);
                return std::unexpected(std::error_code(err, std::generic_category()));
            }

            std::size_t copy_bytes = std::min(size, initial_data.size());
            std::memcpy(ptr, initial_data.data(), copy_bytes);
            ::munmap(ptr, size);
        }

        // Застосовуємо печатки безпеки
        int seal_flags = F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_WRITE | F_SEAL_SEAL;
        if (::fcntl(fd, F_ADD_SEALS, seal_flags) < 0) {
            int err = errno;
            ::close(fd);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        return SealedMemFd(fd, size);
    }

private:
    int fd_{-1};
    std::size_t size_{0};
};

int main() {
    std::string_view payload = "Ідіоматична розділювана пам'ять C++ у shmem";
    auto data_span = std::span<const std::uint8_t>(
        reinterpret_cast<const std::uint8_t*>(payload.data()), payload.size()
    );

    auto result = SealedMemFd::create("cpp_sealed_shm", 4096, data_span);
    if (!result) {
        std::cerr << "Помилка створення memfd: " << result.error().message() << '\n';
        return 1;
    }

    const auto& memfd = *result;
    std::cout << "Успішно створено C++ RAII SealedMemFd дескриптор: " 
              << memfd.native_handle() << " розміром " << memfd.size() << " байтів\n";

    // Спроба змінити розмір опечатаного файла поверне EPERM
    if (::ftruncate(memfd.native_handle(), 8192) < 0) {
        std::cout << "Перевірка печатки C++ успішна: ftruncate заблоковано ядром ("
                  << std::strerror(errno) << ")\n";
    }

    return 0;
}
