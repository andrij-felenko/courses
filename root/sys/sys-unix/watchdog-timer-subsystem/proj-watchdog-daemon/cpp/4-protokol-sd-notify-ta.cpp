// Відправка протокольного повідомлення в systemd notify socket (C++ API)
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <cstdlib>
#include <cstring>
#include <string_view>
#include <system_error>

void notify_systemd_watchdog_cpp() {
    const char* socket_path = std::getenv("NOTIFY_SOCKET");
    if (!socket_path) return;

    int fd = ::socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (fd < 0) return;

    struct sockaddr_un addr{};
    addr.sun_family = AF_UNIX;
    if (socket_path[0] == '@') {
        addr.sun_path[0] = '\0';
        std::strncpy(addr.sun_path + 1, socket_path + 1, sizeof(addr.sun_path) - 2);
    } else {
        std::strncpy(addr.sun_path, socket_path, sizeof(addr.sun_path) - 1);
    }

    constexpr std::string_view msg = "WATCHDOG=1\nREADY=1";
    ::sendto(fd, msg.data(), msg.size(), 0, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr));
    ::close(fd);
}
