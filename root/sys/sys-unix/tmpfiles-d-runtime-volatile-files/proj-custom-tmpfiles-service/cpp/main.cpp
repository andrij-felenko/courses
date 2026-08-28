// C++20 — Ідіоматична реалізація з RAII та обробкою помилок
#include <iostream>
#include <string_view>
#include <filesystem>
#include <system_error>
#include <expected>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>

namespace fs = std::filesystem;

class ScopedUnixSocket {
public:
    explicit ScopedUnixSocket(int fd, fs::path socket_path)
        : fd_(fd), path_(std::move(socket_path)) {}

    ~ScopedUnixSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        std::error_code ec;
        fs::remove(path_, ec);
    }

    ScopedUnixSocket(const ScopedUnixSocket&) = delete;
    ScopedUnixSocket& operator=(const ScopedUnixSocket&) = delete;

    ScopedUnixSocket(ScopedUnixSocket&& other) noexcept
        : fd_(other.fd_), path_(std::move(other.path_)) {
        other.fd_ = -1;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }
    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    int fd_{-1};
    fs::path path_;
};

std::expected<ScopedUnixSocket, std::string> create_server_socket(const fs::path& socket_path) {
    std::error_code ec;
    fs::remove(socket_path, ec);

    int fd = ::socket(AF_UNIX, SOCK_STREAM, 0);
    if (fd < 0) {
        return std::unexpected("Failed to create AF_UNIX socket");
    }

    sockaddr_un addr{};
    addr.sun_family = AF_UNIX;
    if (socket_path.string().length() >= sizeof(addr.sun_path)) {
        ::close(fd);
        return std::unexpected("Socket path is too long");
    }
    std::copy(socket_path.string().begin(), socket_path.string().end(), addr.sun_path);

    if (::bind(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
        ::close(fd);
        return std::unexpected("Failed to bind socket to path: " + socket_path.string());
    }

    fs::permissions(socket_path, 
                    fs::perms::owner_read | fs::perms::owner_write |
                    fs::perms::group_read | fs::perms::group_write,
                    fs::perm_options::replace, ec);
    if (ec) {
        ::close(fd);
        fs::remove(socket_path, ec);
        return std::unexpected("Failed to set socket permissions: " + ec.message());
    }

    if (::listen(fd, 5) < 0) {
        ::close(fd);
        fs::remove(socket_path, ec);
        return std::unexpected("Failed to listen on socket");
    }

    return ScopedUnixSocket(fd, socket_path);
}

int main() {
    const fs::path socket_path = "/run/appdaemon/service.sock";
    std::cout << "Starting appdaemon C++ engine...\n";

    auto server_socket = create_server_socket(socket_path);
    if (!server_socket) {
        std::cerr << "Initialization error: " << server_socket.error() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "Daemon is listening safely on " << server_socket->path() << '\n';

    // Автоматичне очищення сокета та файлового дескриптора при виході завдяки RAII
    return EXIT_SUCCESS;
}
