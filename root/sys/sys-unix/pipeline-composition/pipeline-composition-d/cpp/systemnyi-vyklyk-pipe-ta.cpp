#include <iostream>
#include <array>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>

std::array<int, 2> create_cpp_pipe() {
    std::array<int, 2> fds{-1, -1};
    if (::pipe2(fds.data(), O_CLOEXEC) == -1) {
        throw std::system_error(errno, std::generic_category(), "pipe2 failed");
    }
    std::cout << "Read FD: " << fds[0] << ", Write FD: " << fds[1] << "\n";
    return fds;
}
