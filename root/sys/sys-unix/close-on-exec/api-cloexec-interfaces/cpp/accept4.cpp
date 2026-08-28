#include <sys/socket.h>
#include <netinet/in.h>
#include <system_error>
#include <unistd.h>

int create_bound_server_socket(int port) {
    int fd = ::socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (fd == -1) {
        throw std::system_error(errno, std::generic_category(), "socket creation failed");
    }

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (::bind(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == -1) {
        ::close(fd);
        throw std::system_error(errno, std::generic_category(), "bind failed");
    }
    return fd;
}
