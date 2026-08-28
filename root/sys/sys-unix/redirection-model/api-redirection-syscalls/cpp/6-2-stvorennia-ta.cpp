#include <iostream>
#include <utility>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>

struct PipePair {
    int read_fd{-1};
    int write_fd{-1};

    ~PipePair() {
        if (read_fd >= 0) ::close(read_fd);
        if (write_fd >= 0) ::close(write_fd);
    }
};

std::pair<PipePair, std::error_code> create_safe_pipe() {
    int fds[2];
    if (::pipe2(fds, O_CLOEXEC) < 0) {
        return {{}, std::error_code(errno, std::generic_category())};
    }
    return {PipePair{fds[0], fds[1]}, {}};
}
