#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <cstdlib>
#include <cstring>
#include <cstddef>
#include <string_view>
#include <expected>
#include <system_error>

// Автономна відправка сповіщення в systemd засобами стандарту C++23
[[nodiscard]] std::expected<bool, std::error_code> standalone_sd_notify(std::string_view state) noexcept {
    if (state.empty()) {
        return false;
    }

    const char* socket_path = std::getenv("NOTIFY_SOCKET");
    if (!socket_path) {
        return false; // Службу запущено поза менеджером systemd
    }

    struct sockaddr_un addr{};
    addr.sun_family = AF_UNIX;

    const size_t path_len = std::strlen(socket_path);
    if (path_len >= sizeof(addr.sun_path)) {
        return std::unexpected(std::make_error_code(std::errc::filename_too_long));
    }

    // Обробка абстрактних сокетів Linux
    if (socket_path[0] == '@') {
        addr.sun_path[0] = '\0';
        std::memcpy(&addr.sun_path[1], &socket_path[1], path_len - 1);
    } else {
        std::memcpy(addr.sun_path, socket_path, path_len);
    }

    const int fd = ::socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    const auto addr_len = static_cast<socklen_t>(offsetof(struct sockaddr_un, sun_path) + path_len);
    const ssize_t written = ::sendto(fd, state.data(), state.size(), MSG_NOSIGNAL,
                                     reinterpret_cast<struct sockaddr*>(&addr), addr_len);

    const int saved_errno = errno;
    ::close(fd);

    if (written < 0) {
        return std::unexpected(std::error_code(saved_errno, std::generic_category()));
    }

    return true;
}
