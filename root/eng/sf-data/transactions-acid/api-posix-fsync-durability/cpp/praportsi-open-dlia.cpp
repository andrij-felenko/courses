#include <fcntl.h>
#include <unistd.h>
#include <memory>
#include <string_view>
#include <system_error>

struct FdDeleter {
    void operator()(int* fd_ptr) const noexcept {
        if (fd_ptr && *fd_ptr >= 0) {
            ::close(*fd_ptr);
            delete fd_ptr;
        }
    }
};

using ScopedFd = std::unique_ptr<int, FdDeleter>;

ScopedFd open_synchronous_wal(std::string_view path) {
    int fd = ::open(path.data(), O_WRONLY | O_CREAT | O_DSYNC, 0644);
    if (fd < 0) {
        throw std::system_error(errno, std::generic_category(), "open failed");
    }
    return ScopedFd(new int(fd));
}
