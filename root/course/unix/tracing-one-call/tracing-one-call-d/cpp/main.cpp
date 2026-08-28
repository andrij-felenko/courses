#include <unistd.h>
#include <cerrno>
#include <span>
#include <system_error>
#include <expected>

std::expected<size_t, std::error_code> write_all(int fd, std::span<const char> data)
{
    size_t written = 0;

    while (written < data.size()) {
        ssize_t res = ::write(fd, data.data() + written, data.size() - written);
        if (res < 0) {
            if (errno == EINTR)
                continue; /* Переривання сигналом: повторюємо спробу */
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        if (res == 0)
            break;
        written += static_cast<size_t>(res);
    }
    return written;
}
