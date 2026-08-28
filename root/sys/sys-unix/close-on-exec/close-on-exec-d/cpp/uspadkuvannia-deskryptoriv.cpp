#include <unistd.h>
#include <fcntl.h>
#include <array>
#include <system_error>

void redirect_and_exec() {
    int fd = ::open("output.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        throw std::system_error(errno, std::generic_category(), "open failed");
    }

    if (::dup2(fd, STDOUT_FILENO) < 0) {
        ::close(fd);
        throw std::system_error(errno, std::generic_category(), "dup2 failed");
    }
    ::close(fd);

    std::array<char*, 3> args = { const_cast<char*>("ls"), const_cast<char*>("-la"), nullptr };
    ::execve("/bin/ls", args.data(), nullptr);
}
