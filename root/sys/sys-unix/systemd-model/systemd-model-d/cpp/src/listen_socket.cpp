#include "listen_socket.hpp"

#include <systemd/sd-daemon.h>

#include <fcntl.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>

#include <cerrno>
#include <cstring>
#include <string>
#include <utility>

namespace {

std::error_code errno_code() { return {errno, std::system_category()}; }

// libsystemd повертає -errno у коді результату, а не через errno.
std::error_code sd_code(int r) { return {-r, std::generic_category()}; }

std::error_code make_nonblocking(int fd) {
    const int flags = ::fcntl(fd, F_GETFL, 0);
    if (flags < 0) {
        return errno_code();
    }
    if ((flags & O_NONBLOCK) == 0 && ::fcntl(fd, F_SETFL, flags | O_NONBLOCK) < 0) {
        return errno_code();
    }
    return {};
}

// Запуск без менеджера: піднімаємо такий самий сокет самі.
std::expected<UniqueFd, std::error_code> bind_own(const std::filesystem::path& path) {
    const std::string text = path.string();
    sockaddr_un addr{};

    if (text.empty() || text.size() >= sizeof addr.sun_path) {
        return std::unexpected(std::make_error_code(std::errc::filename_too_long));
    }

    std::error_code ec;
    std::filesystem::create_directories(path.parent_path(), ec);
    // Мертвий вузол сокета після падіння дав би bind() помилку EADDRINUSE,
    // хоч слухати вже нікому.
    std::filesystem::remove(path, ec);

    UniqueFd fd{::socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC | SOCK_NONBLOCK, 0)};
    if (!fd) {
        return std::unexpected(errno_code());
    }

    addr.sun_family = AF_UNIX;
    std::memcpy(addr.sun_path, text.c_str(), text.size());

    if (::bind(fd.get(), reinterpret_cast<const sockaddr*>(&addr), sizeof addr) < 0) {
        return std::unexpected(errno_code());
    }
    // Те, що менеджер зробив би директивою SocketMode=.
    if (::chmod(text.c_str(), 0660) < 0) {
        return std::unexpected(errno_code());
    }
    if (::listen(fd.get(), SOMAXCONN) < 0) {
        return std::unexpected(errno_code());
    }
    // Дескриптор закриє UniqueFd, якщо звідси вилетить помилка: жодного
    // close() у гілках і жодного шансу забути про нього.
    return std::move(fd);
}

}  // namespace

std::expected<ListenSocket, std::error_code> ListenSocket::acquire(
    const std::filesystem::path& fallback_path) {
    // Нуль: після читання прибрати LISTEN_FDS і LISTEN_PID зі середовища,
    // щоб наші нащадки не сприйняли чужі дескриптори як свої.
    const int n = sd_listen_fds(0);
    if (n < 0) {
        return std::unexpected(sd_code(n));
    }

    if (n == 0) {
        auto own = bind_own(fallback_path);
        if (!own) {
            return std::unexpected(own.error());
        }
        return ListenSocket{std::move(*own), Source::Own, fallback_path};
    }

    if (n > 1) {
        // Юніт описує рівно один Listen*=; кілька дескрипторів означають, що
        // сокет-юніт і бінарник розійшлися.
        return std::unexpected(std::make_error_code(std::errc::argument_list_too_long));
    }

    // Перший переданий дескриптор завжди має номер 3: нуль, один і два
    // лишаються стандартним потокам.
    const int fd = SD_LISTEN_FDS_START;

    const int kind = sd_is_socket_unix(fd, SOCK_STREAM, 1, nullptr, 0);
    if (kind < 0) {
        return std::unexpected(sd_code(kind));
    }
    if (kind == 0) {
        return std::unexpected(std::make_error_code(std::errc::wrong_protocol_type));
    }

    // Менеджер віддає сокет блокуючим — циклу на epoll потрібен O_NONBLOCK.
    if (const auto ec = make_nonblocking(fd)) {
        return std::unexpected(ec);
    }

    return ListenSocket{UniqueFd{fd}, Source::Systemd, std::nullopt};
}

ListenSocket::ListenSocket(ListenSocket&& other) noexcept
    : fd_{std::move(other.fd_)},
      source_{other.source_},
      owned_path_{std::exchange(other.owned_path_, std::nullopt)} {}

ListenSocket& ListenSocket::operator=(ListenSocket&& other) noexcept {
    if (this != &other) {
        fd_ = std::move(other.fd_);
        source_ = other.source_;
        owned_path_ = std::exchange(other.owned_path_, std::nullopt);
    }
    return *this;
}

ListenSocket::~ListenSocket() {
    if (owned_path_) {
        std::error_code ec;
        std::filesystem::remove(*owned_path_, ec);
    }
}
