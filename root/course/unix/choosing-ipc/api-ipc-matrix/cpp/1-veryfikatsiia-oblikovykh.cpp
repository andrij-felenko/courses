#include <sys/socket.h>
#include <sys/un.h>
#include <iostream>
#include <expected>
#include <string_view>

std::expected<struct ucred, std::string_view> get_peer_credentials(int client_sock_fd) {
    struct ucred cred{};
    socklen_t len = sizeof(cred);
    if (::getsockopt(client_sock_fd, SOL_SOCKET, SO_PEERCRED, &cred, &len) == -1) {
        return std::unexpected("failed to retrieve SO_PEERCRED");
    }
    return cred;
}
