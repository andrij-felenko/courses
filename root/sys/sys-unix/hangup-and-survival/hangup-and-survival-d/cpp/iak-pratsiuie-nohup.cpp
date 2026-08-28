#include <unistd.h>
#include <fcntl.h>
#include <system_error>

int null_fd = ::open("/dev/null", O_RDONLY);
if (null_fd < 0) {
    throw std::system_error(errno, std::generic_category(), "open /dev/null failed");
}
::dup2(null_fd, STDIN_FILENO);
::close(null_fd);
