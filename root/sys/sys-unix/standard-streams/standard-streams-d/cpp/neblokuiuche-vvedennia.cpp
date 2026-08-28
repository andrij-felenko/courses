#include <fcntl.h>
#include <unistd.h>
#include <system_error>

void set_stdin_nonblocking() {
    int flags = ::fcntl(STDIN_FILENO, F_GETFL, 0);
    if (flags == -1) {
        throw std::system_error(errno, std::generic_category(), "fcntl F_GETFL failed");
    }
    if (::fcntl(STDIN_FILENO, F_SETFL, flags | O_NONBLOCK) == -1) {
        throw std::system_error(errno, std::generic_category(), "fcntl F_SETFL failed");
    }
}
