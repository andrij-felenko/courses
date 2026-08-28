#include <iostream>
#include <array>
#include <string_view>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/prctl.h>
#include <sys/wait.h>
#include <grp.h>

namespace security {

constexpr uid_t kUnprivilegedUid = 65534; // nobody
constexpr gid_t kUnprivilegedGid = 65534; // nogroup

enum class Command : int32_t {
    LogMessage = 1,
    AuthCheck  = 2,
    Exit       = 3
};

struct alignas(8) IpcPacket {
    Command command{Command::LogMessage};
    int32_t payload_len{0};
    std::array<char, 256> buffer{};
};

// RAII-обгортка для файлового дескриптора
class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_(-1) {}
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
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

// Безпечне скидання привілеїв процесу
[[nodiscard]] auto drop_privileges() noexcept -> std::expected<void, std::error_code> {
    if (::setgroups(0, nullptr) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    if (::setresgid(kUnprivilegedGid, kUnprivilegedGid, kUnprivilegedGid) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    if (::setresuid(kUnprivilegedUid, kUnprivilegedUid, kUnprivilegedUid) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

void run_sandboxed_worker(UniqueFd ipc_socket) {
    if (auto res = drop_privileges(); !res) {
        std::cerr << "Помилка деескалації воркера: " << res.error().message() << '\n';
        ::_exit(1);
    }

    IpcPacket packet{};
    packet.command = Command::LogMessage;
    
    constexpr std::string_view msg = "Подія оброблена в C++ RAII пісочниці";
    packet.payload_len = static_cast<int32_t>(msg.size());
    std::memcpy(packet.buffer.data(), msg.data(), msg.size());

    const auto written = ::write(ipc_socket.get(), &packet, sizeof(packet));
    if (written != sizeof(packet)) {
        ::_exit(1);
    }

    ::_exit(0);
}

void run_privileged_monitor(UniqueFd ipc_socket, pid_t worker_pid) {
    IpcPacket packet{};
    const auto read_bytes = ::read(ipc_socket.get(), &packet, sizeof(packet));

    if (read_bytes == sizeof(packet) && packet.command == Command::LogMessage) {
        std::string_view msg_view(packet.buffer.data(), 
                                  std::min<size_t>(packet.payload_len, packet.buffer.size() - 1));
        std::cout << "[MONITOR LOG] Подія від PID " << worker_pid << ": " << msg_view << '\n';
    }

    ipc_socket.reset();

    int status = 0;
    ::waitpid(worker_pid, &status, 0);
}

} // namespace security

int main() {
    std::array<int, 2> sv{-1, -1};
    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, sv.data()) == -1) {
        std::cerr << "socketpair failed: " << std::strerror(errno) << '\n';
        return 1;
    }

    security::UniqueFd monitor_fd(sv[0]);
    security::UniqueFd worker_fd(sv[1]);

    const pid_t pid = ::fork();
    if (pid < 0) {
        std::cerr << "fork failed: " << std::strerror(errno) << '\n';
        return 1;
    }

    if (pid == 0) {
        monitor_fd.reset();
        security::run_sandboxed_worker(std::move(worker_fd));
    } else {
        worker_fd.reset();
        security::run_privileged_monitor(std::move(monitor_fd), pid);
    }

    return 0;
}
