#include <iostream>
#include <csignal>
#include <cerrno>
#include <system_error>
#include <unistd.h>

void handle_cpp_sigpipe(int write_fd) {
    // Ігноруємо SIGPIPE на рівні процесу
    std::signal(SIGPIPE, SIG_IGN);

    std::string data = "Data packet\n";
    ssize_t res = ::write(write_fd, data.data(), data.size());
    if (res == -1) {
        if (errno == EPIPE) {
            std::cerr << "Reader closed the pipe! EPIPE detected.\n";
        } else {
            throw std::system_error(errno, std::generic_category(), "write failed");
        }
    }
}
