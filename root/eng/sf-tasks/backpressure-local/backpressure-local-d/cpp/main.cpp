#include <unistd.h>
#include <fcntl.h>
#include <cerrno>
#include <span>
#include <expected>
#include <system_error>

enum class IoStatus {
    Backpressure, // Буфер ядра повний (EAGAIN/EWOULDBLOCK)
    BrokenPipe,   // Канал закрито на стороні читача (EPIPE)
    SysError      // Інша помилка ОС
};

// Ідіоматична обробка неблокуючого протитиску засобами сучасного C++
std::expected<size_t, IoStatus> safe_write_with_backpressure(int fd, std::span<const std::byte> data) {
    size_t written = 0;

    while (written < data.size()) {
        ssize_t res = ::write(fd, data.data() + written, data.size() - written);
        if (res > 0) {
            written += static_cast<size_t>(res);
            continue;
        }
        if (res == -1) {
            if (errno == EINTR) continue;
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                if (written > 0) return written;
                return std::unexpected(IoStatus::Backpressure);
            }
            if (errno == EPIPE) {
                return std::unexpected(IoStatus::BrokenPipe);
            }
            return std::unexpected(IoStatus::SysError);
        }
    }
    return written;
}
