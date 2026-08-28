#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <chrono>
#include <atomic>
#include <expected>
#include <span>
#include <array>
#include <csignal>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <sys/signalfd.h>
#include <sys/timerfd.h>
#include <netinet/in.h>
#include <arpa/inet.h>

namespace net {

/* RAII-обгортка над файловим дескриптором ядра */
class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_(-1) {}
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

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
        int tmp = fd_;
        fd_ = -1;
        return tmp;
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

enum class ServerState {
    Running,
    Stopping,
    Draining,
    Done,
    Timeout
};

class GracefulServer {
public:
    explicit GracefulServer(int port, std::chrono::seconds drain_timeout = std::chrono::seconds(5))
        : port_(port), timeout_duration_(drain_timeout), state_(ServerState::Running) {}

    [[nodiscard]] bool initialize() {
        epoll_fd_.reset(::epoll_create1(EPOLL_CLOEXEC));
        if (!epoll_fd_.valid()) {
            std::perror("epoll_create1");
            return false;
        }

        auto sfd = setup_signalfd();
        if (!sfd) return false;
        signal_fd_ = std::move(*sfd);

        auto tfd = setup_timerfd();
        if (!tfd) return false;
        timer_fd_ = std::move(*tfd);

        auto lfd = setup_listen_socket();
        if (!lfd) return false;
        listen_fd_ = std::move(*lfd);

        add_to_epoll(signal_fd_.get(), EPOLLIN);
        add_to_epoll(timer_fd_.get(), EPOLLIN);
        add_to_epoll(listen_fd_.get(), EPOLLIN);

        std::cout << "[CPP-SERVER] Ініціалізація завершена. Порт: " << port_
                  << ", PID: " << ::getpid() << '\n';
        return true;
    }

    int run() {
        constexpr size_t max_events = 64;
        std::array<epoll_event, max_events> events{};
        std::array<char, 1024> buffer{};

        while (state_ != ServerState::Done && state_ != ServerState::Timeout) {
            int nfds = ::epoll_wait(epoll_fd_.get(), events.data(), max_events, -1);
            if (nfds == -1) {
                if (errno == EINTR) continue;
                std::perror("epoll_wait");
                break;
            }

            for (int i = 0; i < nfds; ++i) {
                int current_fd = events[i].data.fd;

                if (current_fd == signal_fd_.get()) {
                    handle_signal_event();
                } else if (current_fd == timer_fd_.get()) {
                    handle_timer_timeout();
                } else if (current_fd == listen_fd_.get()) {
                    handle_new_connection();
                } else {
                    handle_client_io(current_fd, buffer);
                }
            }
        }

        return perform_final_cleanup();
    }

private:
    std::expected<UniqueFd, int> setup_signalfd() {
        sigset_t mask;
        sigemptyset(&mask);
        sigaddset(&mask, SIGTERM);
        sigaddset(&mask, SIGINT);

        if (::pthread_sigmask(SIG_BLOCK, &mask, nullptr) != 0) {
            std::perror("pthread_sigmask");
            return std::unexpected(errno);
        }

        int fd = ::signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
        if (fd == -1) {
            std::perror("signalfd");
            return std::unexpected(errno);
        }
        return UniqueFd(fd);
    }

    std::expected<UniqueFd, int> setup_timerfd() {
        int fd = ::timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC);
        if (fd == -1) {
            std::perror("timerfd_create");
            return std::unexpected(errno);
        }
        return UniqueFd(fd);
    }

    std::expected<UniqueFd, int> setup_listen_socket() {
        int fd = ::socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
        if (fd == -1) {
            std::perror("socket");
            return std::unexpected(errno);
        }

        int opt = 1;
        ::setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = htonl(INADDR_ANY);
        addr.sin_port = htons(port_);

        if (::bind(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == -1) {
            std::perror("bind");
            return std::unexpected(errno);
        }

        if (::listen(fd, SOMAXCONN) == -1) {
            std::perror("listen");
            return std::unexpected(errno);
        }
        return UniqueFd(fd);
    }

    void add_to_epoll(int fd, uint32_t events_mask) {
        epoll_event ev{};
        ev.events = events_mask;
        ev.data.fd = fd;
        ::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_ADD, fd, &ev);
    }

    void remove_from_epoll(int fd) {
        ::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_DEL, fd, nullptr);
    }

    void arm_drain_watchdog() {
        itimerspec its{};
        its.it_value.tv_sec = timeout_duration_.count();
        its.it_value.tv_nsec = 0;
        ::timerfd_settime(timer_fd_.get(), 0, &its, nullptr);
    }

    void handle_signal_event() {
        signalfd_siginfo fdsi{};
        ssize_t s = ::read(signal_fd_.get(), &fdsi, sizeof(fdsi));
        if (s != sizeof(fdsi)) return;

        std::cout << "\n[CPP-SERVER] Отримано сигнал " << fdsi.ssi_signo
                  << " від процесу PID " << fdsi.ssi_pid << '\n';

        if (state_ == ServerState::Running) {
            std::cout << "[CPP-SERVER] Початок дренування. Зупинка прийому нових з'єднань...\n";
            state_ = ServerState::Stopping;

            remove_from_epoll(listen_fd_.get());
            listen_fd_.reset(); // Закриття сокету прослуховування

            arm_drain_watchdog();
            state_ = ServerState::Draining;

            if (active_connections_.empty()) {
                std::cout << "[CPP-SERVER] Немає активних сесій. Миттєвий вихід.\n";
                state_ = ServerState::Done;
            } else {
                std::cout << "[CPP-SERVER] Очікування завершення "
                          << active_connections_.size() << " активних з'єднань...\n";
            }
        } else if (state_ == ServerState::Draining) {
            std::cout << "[CPP-SERVER] Повторний сигнал! Форсоване переривання.\n";
            state_ = ServerState::Timeout;
        }
    }

    void handle_timer_timeout() {
        uint64_t expirations = 0;
        ::read(timer_fd_.get(), &expirations, sizeof(expirations));
        std::cerr << "[CPP-SERVER] Таймаут дренування вичерпано! Аварійний скид.\n";
        state_ = ServerState::Timeout;
    }

    void handle_new_connection() {
        sockaddr_in client_addr{};
        socklen_t len = sizeof(client_addr);
        int client_raw = ::accept4(listen_fd_.get(),
                                   reinterpret_cast<sockaddr*>(&client_addr),
                                   &len, SOCK_NONBLOCK | SOCK_CLOEXEC);
        if (client_raw >= 0) {
            add_to_epoll(client_raw, EPOLLIN | EPOLLRDHUP);
            active_connections_.push_back(UniqueFd(client_raw));
            std::cout << "[CPP-CLIENT] Під'єднано клієнта FD " << client_raw
                      << " (всього: " << active_connections_.size() << ")\n";
        }
    }

    void handle_client_io(int client_fd, std::span<char> buf) {
        ssize_t n = ::read(client_fd, buf.data(), buf.size() - 1);
        if (n > 0) {
            buf[n] = '\0';
            std::string_view header = (state_ == ServerState::Draining)
                ? "HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n"
                : "ACK: ";
            ::write(client_fd, header.data(), header.size());
            ::write(client_fd, buf.data(), n);

            if (state_ == ServerState::Draining) {
                ::shutdown(client_fd, SHUT_WR);
            }
        } else {
            remove_from_epoll(client_fd);
            std::erase_if(active_connections_, [client_fd](const UniqueFd& conn) {
                return conn.get() == client_fd;
            });
            std::cout << "[CPP-CLIENT] Сесію FD " << client_fd
                      << " закрито. Залишилося: " << active_connections_.size() << '\n';

            if (state_ == ServerState::Draining && active_connections_.empty()) {
                std::cout << "[CPP-SERVER] Усі клієнти штатно завершили роботу.\n";
                state_ = ServerState::Done;
            }
        }
    }

    int perform_final_cleanup() {
        std::cout << "[CPP-SERVER] Очищення активних ресурсів перед виходом...\n";
        active_connections_.clear(); // RAII закриває всі клієнтські сокети
        listen_fd_.reset();
        signal_fd_.reset();
        timer_fd_.reset();
        epoll_fd_.reset();

        if (state_ == ServerState::Done) {
            std::cout << "[CPP-SERVER] Штатне вимикання завершено успішно (код 0).\n";
            return 0;
        }
        std::cerr << "[CPP-SERVER] Аварійне вимикання через таймаут (код 1).\n";
        return 1;
    }

    int port_;
    std::chrono::seconds timeout_duration_;
    std::atomic<ServerState> state_;
    UniqueFd epoll_fd_;
    UniqueFd signal_fd_;
    UniqueFd timer_fd_;
    UniqueFd listen_fd_;
    std::vector<UniqueFd> active_connections_;
};

} // namespace net

int main(int argc, char* argv[]) {
    int port = (argc > 1) ? std::stoi(argv[1]) : 8080;
    net::GracefulServer server(port);
    if (!server.initialize()) {
        return 1;
    }
    return server.run();
}
