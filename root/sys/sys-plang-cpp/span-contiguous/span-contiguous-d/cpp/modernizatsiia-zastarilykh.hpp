#include <span>
#include <cstddef>
#include <unistd.h>
#include <sys/uio.h>

// Безпечна обгортка над системним викликом write()
ssize_t safe_write(int fd, std::span<const std::byte> data) noexcept {
    return ::write(fd, data.data(), data.size_bytes());
}

// Запис масиву розсіяних зрізів через writev()
ssize_t safe_writev(int fd, std::span<const struct iovec> io_vectors) noexcept {
    return ::writev(fd, io_vectors.data(), static_cast<int>(io_vectors.size()));
}
