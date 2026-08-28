#include <iostream>
#include <string_view>
#include <optional>
#include <system_error>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>

class CustomNotifier {
public:
    static std::optional<std::error_code> notify(std::string_view state) noexcept {
        const char* socket_path = std::getenv("NOTIFY_SOCKET");
        if (!socket_path || *socket_path == '\0') {
            return std::nullopt; // Сокет не налаштовано
        }

        int fd = ::socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
        if (fd < 0) {
            return std::error_code(errno, std::generic_category());
        }

        // RAII обгортка для автоматичного закриття дескриптора сокета
        struct SocketCloser {
            int sock_fd;
            ~SocketCloser() { if (sock_fd >= 0) ::close(sock_fd); }
        } guard{fd};

        struct sockaddr_un addr{};
        addr.sun_family = AF_UNIX;

        size_t path_len = std::strlen(socket_path);
        if (socket_path[0] == '@') {
            addr.sun_path[0] = '\0';
            if (path_len >= sizeof(addr.sun_path)) path_len = sizeof(addr.sun_path) - 1;
            std::memcpy(addr.sun_path + 1, socket_path + 1, path_len - 1);
        } else {
            if (path_len >= sizeof(addr.sun_path)) path_len = sizeof(addr.sun_path) - 1;
            std::memcpy(addr.sun_path, socket_path, path_len);
        }

        socklen_t addr_len = static_cast<socklen_t>(sizeof(sa_family_t) + path_len);
        ssize_t bytes_sent = ::sendto(fd, state.data(), state.size(), MSG_NOSIGNAL,
                                      reinterpret_cast<struct sockaddr*>(&addr), addr_len);

        if (bytes_sent < 0) {
            return std::error_code(errno, std::generic_category());
        }

        return std::nullopt;
    }
};

int main() {
    auto err = CustomNotifier::notify("READY=1\nSTATUS=Idiomatic C++20 Zero-dep notifier.");
    if (err) {
        std::cerr << "Notification error: " << err->message() << "\n";
    } else {
        std::cout << "Notification sent successfully.\n";
    }
    return 0;
}
