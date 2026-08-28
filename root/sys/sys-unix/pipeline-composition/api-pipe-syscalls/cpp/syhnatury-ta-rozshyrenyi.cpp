#include <array>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>

// Ідіоматична C++ обгортка над системними викликами pipe/pipe2
std::array<int, 2> create_pipe_pair(int flags = O_CLOEXEC) {
    std::array<int, 2> pipefd{-1, -1};
    if (::pipe2(pipefd.data(), flags) == -1) {
        throw std::system_error(errno, std::generic_category(), "pipe2 failed");
    }
    return pipefd;
}
