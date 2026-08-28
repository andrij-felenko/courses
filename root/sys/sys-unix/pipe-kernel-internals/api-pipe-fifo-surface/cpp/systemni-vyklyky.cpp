#include <unistd.h>
#include <fcntl.h>
#include <array>
#include <system_error>

std::array<int, 2> create_pipe(int flags = 0) {
    std::array<int, 2> fds{-1, -1};
    if (::pipe2(fds.data(), flags) < 0) {
        throw std::system_error(errno, std::generic_category(), "pipe2 failed");
    }
    return fds;
}
