#include <unistd.h>
#include <fcntl.h>
#include <system_error>

void sanitize_descriptors_raii() {
    int null_fd = ::open("/dev/null", O_RDWR);
    if (null_fd < 0) {
        throw std::system_error(errno, std::generic_category(), "Failed to open /dev/null");
    }

    ::dup2(null_fd, STDIN_FILENO);
    ::dup2(null_fd, STDOUT_FILENO);
    ::dup2(null_fd, STDERR_FILENO);

    if (null_fd > STDERR_FILENO) {
        ::close(null_fd);
    }
}
