#include <sys/ioctl.h>
#include <linux/fs.h>
#include <expected>
#include <system_error>
#include <cerrno>

[[nodiscard]] std::expected<void, std::error_code>
clone_file_blocks(int src_fd, int dest_fd) {
    if (::ioctl(dest_fd, FICLONE, src_fd) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
