#include <filesystem>
#include <fstream>
#include <string>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>

namespace fs = std::filesystem;

class OpenSpaceRescuer {
public:
    static std::error_code truncate_deleted_fd(pid_t pid, int target_fd) noexcept {
        const std::string proc_path = "/proc/" + std::to_string(pid) + "/fd/" + std::to_string(target_fd);

        int fd = ::open(proc_path.c_str(), O_WRONLY);
        if (fd < 0) {
            return std::error_code(errno, std::generic_category());
        }

        if (::ftruncate(fd, 0) != 0) {
            const int err = errno;
            ::close(fd);
            return std::error_code(err, std::generic_category());
        }

        ::close(fd);
        return {};
    }
};
