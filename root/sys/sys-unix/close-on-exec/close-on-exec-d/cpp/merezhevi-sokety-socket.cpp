#include <sys/socket.h>
#include <netinet/in.h>
#include <system_error>

int create_listening_socket() {
    int fd = ::socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (fd == -1) {
        throw std::system_error(errno, std::generic_category(), "socket failed");
    }
    return fd;
}

int accept_client_connection(int listen_fd) {
    int client_fd = ::accept4(listen_fd, nullptr, nullptr, SOCK_CLOEXEC);
    if (client_fd == -1) {
        throw std::system_error(errno, std::generic_category(), "accept4 failed");
    }
    return client_fd;
}
