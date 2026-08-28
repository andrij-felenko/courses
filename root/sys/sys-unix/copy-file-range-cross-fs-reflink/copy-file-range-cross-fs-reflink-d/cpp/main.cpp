// Ідіоматичний підхід C++ із використання RAII та std::expected
#include <expected>
#include <system_error>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/fs.h>

#ifndef FICLONE
#define FICLONE _IOW(0x94, 9, int)
#endif

namespace fs_utils {

[[nodiscard]] std::expected<void, std::error_code> copy_file_cascading(
    int fd_in, int fd_out, size_t file_size) noexcept 
{
    // 1. Спроба Reflink (FICLONE)
    if (::ioctl(fd_out, FICLONE, fd_in) == 0) {
        return {}; // Миттєве CoW клонування метаданих
    }

    // 2. Спроба copy_file_range (Cross-FS offload)
    loff_t off_in = 0, off_out = 0;
    size_t remaining = file_size;

    while (remaining > 0) {
        ssize_t ret = ::copy_file_range(fd_in, &off_in, fd_out, &off_out, remaining, 0);
        if (ret > 0) {
            remaining -= static_cast<size_t>(ret);
            continue;
        }
        if (ret == 0) break; // EOF
        if (errno == EINTR) continue;

        if (errno == EXDEV || errno == EOPNOTSUPP || errno == ENOSYS || errno == EINVAL) {
            break; // Перехід до POSIX fallback
        }
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (remaining == 0) return {};

    // 3. Завершальний фолбек — продовжуємо з досягнутих зміщень
    return fallback_read_write_loop(fd_in, &off_in, fd_out, &off_out, remaining);
}

} // namespace fs_utils
