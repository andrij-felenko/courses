#include <fcntl.h>
#include <system_error>

int open_readonly_cloexec(const char* path) {
    int fd = ::open(path, O_RDONLY | O_CLOEXEC);
    if (fd == -1) {
        throw std::system_error(errno, std::generic_category(), "open failed");
    }
    return fd;
}
