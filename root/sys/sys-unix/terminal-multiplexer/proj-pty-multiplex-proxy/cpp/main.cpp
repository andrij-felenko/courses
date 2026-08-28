#include <iostream>
#include <string_view>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <pty.h>
#include <termios.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/wait.h>
#include <poll.h>

namespace miniplex {

constexpr std::string_view kSocketPath = "/tmp/miniplex.sock";
constexpr char kDetachKey = 0x1d; // Ctrl+]
constexpr size_t kBufferSize = 4096;

enum class ErrorCode {
    PtyCreationFailed,
    ForkFailed,
    SocketCreationFailed,
    BindFailed,
    ListenFailed,
    ConnectFailed,
    TerminalConfigFailed,
    IoError
};

std::error_code make_error_code(ErrorCode e) {
    return {static_cast<int>(e), std::generic_category()};
}

class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_{-1} {}
    explicit UniqueFd(int fd) noexcept : fd_{fd} {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_{other.release()} {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        reset(other.release());
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_;
};

class RawTerminalGuard {
public:
    static std::expected<RawTerminalGuard, ErrorCode> create() {
        struct termios orig;
        if (::tcgetattr(STDIN_FILENO, &orig) < 0) {
            return std::unexpected(ErrorCode::TerminalConfigFailed);
        }
        struct termios raw = orig;
        raw.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
        raw.c_oflag &= ~(OPOST);
        raw.c_cflag |= (CS8);
        raw.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
        raw.c_cc[VMIN] = 1;
        raw.c_cc[VTIME] = 0;

        if (::tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) < 0) {
            return std::unexpected(ErrorCode::TerminalConfigFailed);
        }
        return RawTerminalGuard(orig);
    }

    ~RawTerminalGuard() {
        if (active_) {
            ::tcsetattr(STDIN_FILENO, TCSAFLUSH, &orig_termios_);
        }
    }

    RawTerminalGuard(const RawTerminalGuard&) = delete;
    RawTerminalGuard& operator=(const RawTerminalGuard&) = delete;
    RawTerminalGuard(RawTerminalGuard&& other) noexcept
        : orig_termios_{other.orig_termios_}, active_{other.active_} {
        other.active_ = false;
    }

private:
    explicit RawTerminalGuard(const struct termios& orig)
        : orig_termios_{orig}, active_{true} {}

    struct termios orig_termios_{};
    bool active_{false};
};

enum class TransferStatus {
    Ok,
    Detached,
    Closed,
    Error
};

TransferStatus forward_stream(int src_fd, int dst_fd, bool check_detach) {
    std::vector<char> buffer(kBufferSize);
    ssize_t n = ::read(src_fd, buffer.data(), buffer.size());
    if (n <= 0) {
        return (n == 0) ? TransferStatus::Closed : TransferStatus::Error;
    }

    std::span<const char> bytes(buffer.data(), static_cast<size_t>(n));
    if (check_detach) {
        for (char b : bytes) {
            if (b == kDetachKey) {
                return TransferStatus::Detached;
            }
        }
    }

    size_t written = 0;
    while (written < bytes.size()) {
        ssize_t res = ::write(dst_fd, bytes.data() + written, bytes.size() - written);
        if (res < 0) {
            if (errno == EINTR) continue;
            return TransferStatus::Error;
        }
        written += static_cast<size_t>(res);
    }
    return TransferStatus::Ok;
}

std::expected<void, ErrorCode> run_server() {
    int raw_master_fd = -1;
    pid_t pid = ::forkpty(&raw_master_fd, nullptr, nullptr, nullptr);
    if (pid < 0) {
        return std::unexpected(ErrorCode::ForkFailed);
    }
    if (pid == 0) {
        ::execl("/bin/sh", "sh", nullptr);
        ::_exit(127);
    }

    UniqueFd master_fd(raw_master_fd);
    ::unlink(kSocketPath.data());

    UniqueFd listen_fd(::socket(AF_UNIX, SOCK_STREAM, 0));
    if (!listen_fd.valid()) {
        return std::unexpected(ErrorCode::SocketCreationFailed);
    }

    struct sockaddr_un addr{};
    addr.sun_family = AF_UNIX;
    std::strncpy(addr.sun_path, kSocketPath.data(), sizeof(addr.sun_path) - 1);

    if (::bind(listen_fd.get(), reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
        return std::unexpected(ErrorCode::BindFailed);
    }
    if (::listen(listen_fd.get(), 1) < 0) {
        return std::unexpected(ErrorCode::ListenFailed);
    }

    while (true) {
        UniqueFd client_fd(::accept(listen_fd.get(), nullptr, nullptr));
        if (!client_fd.valid()) {
            if (errno == EINTR) continue;
            break;
        }

        std::vector<struct pollfd> fds(2);
        fds[0].fd = master_fd.get();
        fds[0].events = POLLIN;
        fds[1].fd = client_fd.get();
        fds[1].events = POLLIN;

        bool client_active = true;
        while (client_active) {
            int ret = ::poll(fds.data(), fds.size(), -1);
            if (ret < 0) {
                if (errno == EINTR) continue;
                break;
            }

            if (fds[0].revents & (POLLIN | POLLERR | POLLHUP)) {
                auto status = forward_stream(master_fd.get(), client_fd.get(), false);
                if (status != TransferStatus::Ok) {
                    ::unlink(kSocketPath.data());
                    ::waitpid(pid, nullptr, 0);
                    return {};
                }
            }

            if (fds[1].revents & (POLLIN | POLLERR | POLLHUP)) {
                auto status = forward_stream(client_fd.get(), master_fd.get(), false);
                if (status != TransferStatus::Ok) {
                    client_active = false;
                }
            }
        }
    }
    ::unlink(kSocketPath.data());
    return {};
}

std::expected<void, ErrorCode> run_client() {
    UniqueFd sock_fd(::socket(AF_UNIX, SOCK_STREAM, 0));
    if (!sock_fd.valid()) {
        return std::unexpected(ErrorCode::SocketCreationFailed);
    }

    struct sockaddr_un addr{};
    addr.sun_family = AF_UNIX;
    std::strncpy(addr.sun_path, kSocketPath.data(), sizeof(addr.sun_path) - 1);

    if (::connect(sock_fd.get(), reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
        return std::unexpected(ErrorCode::ConnectFailed);
    }

    auto term_guard = RawTerminalGuard::create();
    if (!term_guard) {
        return std::unexpected(term_guard.error());
    }

    std::vector<struct pollfd> fds(2);
    fds[0].fd = STDIN_FILENO;
    fds[0].events = POLLIN;
    fds[1].fd = sock_fd.get();
    fds[1].events = POLLIN;

    while (true) {
        int ret = ::poll(fds.data(), fds.size(), -1);
        if (ret < 0) {
            if (errno == EINTR) continue;
            break;
        }

        if (fds[0].revents & POLLIN) {
            auto status = forward_stream(STDIN_FILENO, sock_fd.get(), true);
            if (status == TransferStatus::Detached) {
                break;
            }
            if (status != TransferStatus::Ok) break;
        }

        if (fds[1].revents & (POLLIN | POLLERR | POLLHUP)) {
            auto status = forward_stream(sock_fd.get(), STDOUT_FILENO, false);
            if (status != TransferStatus::Ok) break;
        }
    }
    return {};
}

} // namespace miniplex

int main(int argc, char* argv[]) {
    if (argc > 1 && std::string_view(argv[1]) == "--server") {
        if (auto res = miniplex::run_server(); !res) {
            std::cerr << "Помилка сервера miniplex\n";
            return 1;
        }
    } else if (argc > 1 && std::string_view(argv[1]) == "--client") {
        if (auto res = miniplex::run_client(); !res) {
            std::cerr << "Помилка клієнта miniplex\n";
            return 1;
        }
    } else {
        std::cerr << "Ужиток: " << argv[0] << " --server | --client\n";
        return 1;
    }
    return 0;
}
