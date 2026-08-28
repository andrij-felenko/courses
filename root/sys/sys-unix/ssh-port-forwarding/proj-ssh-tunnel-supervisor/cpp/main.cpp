#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <thread>
#include <atomic>
#include <expected>
#include <system_error>
#include <cstring>
#include <csignal>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>

namespace {
    std::atomic<bool> g_running{true};
    std::atomic<bool> g_child_dead{false};

    void signal_handler(int sig) noexcept {
        if (sig == SIGTERM || sig == SIGINT) {
            g_running.store(false);
        } else if (sig == SIGCHLD) {
            g_child_dead.store(true);
        }
    }

    // RAII-обгортка над сокетним файловим дескриптором
    class UniqueFd {
    public:
        constexpr UniqueFd() noexcept : fd_(-1) {}
        explicit constexpr UniqueFd(int fd) noexcept : fd_(fd) {}
        
        ~UniqueFd() {
            reset();
        }

        UniqueFd(const UniqueFd&) = delete;
        UniqueFd& operator=(const UniqueFd&) = delete;

        UniqueFd(UniqueFd&& other) noexcept : fd_(other.fd_) {
            other.fd_ = -1;
        }

        UniqueFd& operator=(UniqueFd&& other) noexcept {
            if (this != &other) {
                reset();
                fd_ = other.fd_;
                other.fd_ = -1;
            }
            return *this;
        }

        [[nodiscard]] constexpr int get() const noexcept { return fd_; }
        [[nodiscard]] constexpr bool valid() const noexcept { return fd_ >= 0; }

        void reset(int new_fd = -1) noexcept {
            if (fd_ >= 0) {
                ::close(fd_);
            }
            fd_ = new_fd;
        }

    private:
        int fd_{-1};
    };

    // RAII-керування процесом
    class ProcessGuard {
    public:
        constexpr ProcessGuard() noexcept : pid_(-1) {}
        explicit constexpr ProcessGuard(pid_t pid) noexcept : pid_(pid) {}

        ~ProcessGuard() {
            terminate();
        }

        ProcessGuard(const ProcessGuard&) = delete;
        ProcessGuard& operator=(const ProcessGuard&) = delete;

        ProcessGuard(ProcessGuard&& other) noexcept : pid_(other.pid_) {
            other.pid_ = -1;
        }

        ProcessGuard& operator=(ProcessGuard&& other) noexcept {
            if (this != &other) {
                terminate();
                pid_ = other.pid_;
                other.pid_ = -1;
            }
            return *this;
        }

        [[nodiscard]] constexpr pid_t get() const noexcept { return pid_; }
        [[nodiscard]] constexpr bool active() const noexcept { return pid_ > 0; }

        void release() noexcept {
            pid_ = -1;
        }

        void terminate() noexcept {
            if (pid_ > 0) {
                ::kill(pid_, SIGTERM);
                int status = 0;
                for (int i = 0; i < 10; ++i) {
                    if (::waitpid(pid_, &status, WNOHANG) > 0) {
                        pid_ = -1;
                        return;
                    }
                    std::this_thread::sleep_for(std::chrono::milliseconds(100));
                }
                ::kill(pid_, SIGKILL);
                ::waitpid(pid_, &status, 0);
                pid_ = -1;
            }
        }

    private:
        pid_t pid_{-1};
    };
}

class TunnelSupervisor {
public:
    TunnelSupervisor(std::string host, int local_port, std::string remote_dest)
        : host_(std::move(host)), local_port_(local_port), remote_dest_(std::move(remote_dest)) {}

    void run() {
        std::cout << "[supervisor++] Запуск для 127.0.0.1:" << local_port_
                  << " -> " << remote_dest_ << " через " << host_ << '\n';

        auto backoff = std::chrono::seconds(2);

        while (g_running.load()) {
            if (!process_.active()) {
                auto start_res = spawn_ssh();
                if (!start_res) {
                    std::cerr << "[supervisor++] Помилка fork: " << start_res.error().message() << '\n';
                    std::this_thread::sleep_for(backoff);
                    backoff = std::min(backoff * 2, std::chrono::seconds(30));
                    continue;
                }
                process_ = ProcessGuard(*start_res);
                g_child_dead.store(false);
                std::this_thread::sleep_for(std::chrono::seconds(2));
            }

            if (g_child_dead.load()) {
                int status = 0;
                pid_t p = ::waitpid(process_.get(), &status, WNOHANG);
                if (p > 0) {
                    std::cout << "[supervisor++] SSH завершився зі статусом " << status << '\n';
                    process_.release();
                    std::this_thread::sleep_for(backoff);
                    continue;
                }
            }

            if (probe_port(std::chrono::milliseconds(1000))) {
                backoff = std::chrono::seconds(2);
                std::this_thread::sleep_for(std::chrono::seconds(5));
            } else {
                std::cout << "[supervisor++] Зонд не вдався! Перезапуск тунелю...\n";
                process_.terminate();
                std::this_thread::sleep_for(backoff);
                backoff = std::min(backoff * 2, std::chrono::seconds(30));
            }
        }

        std::cout << "[supervisor++] Завершення роботи.\n";
    }

private:
    [[nodiscard]] std::expected<pid_t, std::error_code> spawn_ssh() {
        const std::string forward_spec = std::to_string(local_port_) + ":" + remote_dest_;

        pid_t pid = ::fork();
        if (pid < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (pid == 0) {
            std::vector<const char*> args = {
                "ssh",
                "-N",
                "-L", forward_spec.c_str(),
                "-o", "ExitOnForwardFailure=yes",
                "-o", "ServerAliveInterval=15",
                "-o", "ServerAliveCountMax=3",
                "-o", "BatchMode=yes",
                host_.c_str(),
                nullptr
            };
            ::execvp("ssh", const_cast<char* const*>(args.data()));
            ::_exit(127);
        }

        return pid;
    }

    [[nodiscard]] bool probe_port(std::chrono::milliseconds timeout) const {
        UniqueFd sock(::socket(AF_INET, SOCK_STREAM, 0));
        if (!sock.valid()) {
            return false;
        }

        int flags = ::fcntl(sock.get(), F_GETFL, 0);
        if (flags < 0 || ::fcntl(sock.get(), F_SETFL, flags | O_NONBLOCK) < 0) {
            return false;
        }

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(static_cast<uint16_t>(local_port_));
        ::inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

        int res = ::connect(sock.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr));
        if (res == 0) {
            return true;
        }

        if (errno != EINPROGRESS) {
            return false;
        }

        pollfd pfd{};
        pfd.fd = sock.get();
        pfd.events = POLLOUT;

        int poll_res = ::poll(&pfd, 1, static_cast<int>(timeout.count()));
        if (poll_res > 0 && (pfd.revents & POLLOUT)) {
            int err = 0;
            socklen_t len = sizeof(err);
            if (::getsockopt(sock.get(), SOL_SOCKET, SO_ERROR, &err, &len) == 0 && err == 0) {
                return true;
            }
        }

        return false;
    }

    std::string host_;
    int local_port_;
    std::string remote_dest_;
    ProcessGuard process_;
};

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Використання: " << argv[0] << " <ssh_host> <local_port> <remote_host:port>\n";
        return 1;
    }

    struct sigaction sa{};
    sa.sa_handler = signal_handler;
    ::sigaction(SIGTERM, &sa, nullptr);
    ::sigaction(SIGINT, &sa, nullptr);

    struct sigaction sc{};
    sc.sa_handler = signal_handler;
    sc.sa_flags = SA_RESTART | SA_NOCLDSTOP;
    ::sigaction(SIGCHLD, &sc, nullptr);

    ::signal(SIGPIPE, SIG_IGN);

    TunnelSupervisor supervisor(argv[1], std::stoi(argv[2]), argv[3]);
    supervisor.run();

    return 0;
}
