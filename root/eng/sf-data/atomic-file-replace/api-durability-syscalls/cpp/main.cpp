#include <fcntl.h>
#include <unistd.h>
#include <filesystem>
#include <span>
#include <string>
#include <system_error>
#include <expected>

namespace fs = std::filesystem;

class AnonymousTempWriter {
public:
    static std::expected<void, std::error_code> writeAndLink(
        const fs::path& directory,
        const fs::path& target_name,
        std::span<const std::byte> data) noexcept 
    {
        int fd = ::open(directory.c_str(), O_TMPFILE | O_RDWR, 0600);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        struct AutoClose {
            int fd;
            ~AutoClose() { if (fd >= 0) ::close(fd); }
        } guard{fd};

        const auto* ptr = reinterpret_cast<const uint8_t*>(data.data());
        size_t rem = data.size();
        while (rem > 0) {
            ssize_t n = ::write(fd, ptr, rem);
            if (n < 0) {
                if (errno == EINTR) continue;
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }
            ptr += n;
            rem -= static_cast<size_t>(n);
        }

        if (::fsync(fd) != 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        std::string proc_fd = "/proc/self/fd/" + std::to_string(fd);
        fs::path target_full = directory / target_name;
        if (::linkat(AT_FDCWD, proc_fd.c_str(), AT_FDCWD, target_full.c_str(), AT_SYMLINK_FOLLOW) != 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return {};
    }
};
