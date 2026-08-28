// ==========================================================================
// reactor_server.cpp — Ідіоматичний подієвий сервер на C++20 (Linux epoll)
// Компіляція: g++ -O2 -std=c++20 -Wall -Wextra reactor_server.cpp -o reactor_server_cpp
// ==========================================================================

#include <iostream>
#include <vector>
#include <unordered_map>
#include <memory>
#include <span>
#include <string_view>
#include <chrono>
#include <cstring>
#include <cerrno>

#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <sys/timerfd.h>
#include <sys/signalfd.h>
#include <netinet/in.h>
#include <arpa/inet.h>

namespace net {

// RAII обгортка над системним файловим дескриптором
class UniqueFd {
    int fd_{-1};
public:
    constexpr UniqueFd() noexcept = default;
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
    explicit operator bool() const noexcept { return valid(); }

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
};

// Стан клієнтської сесії з динамічним буфером відправки
struct Session {
    UniqueFd socket;
    std::chrono::steady_clock::time_point last_active;
    std::vector<char> out_buffer;

    explicit Session(UniqueFd sock)
        : socket(std::move(sock)), last_active(std::chrono::steady_clock::now()) {}
};

class ReactorServer {
    static constexpr int MaxEvents = 64;
    static constexpr int BufferSize = 4096;
    static constexpr uint16_t Port = 8080;

    UniqueFd epfd_;
    UniqueFd listen_fd_;
    UniqueFd timer_fd_;
    UniqueFd signal_fd_;
    std::unordered_map<int, std::unique_ptr<Session>> sessions_;
    bool running_{false};

public:
    ReactorServer() = default;

    void init() {
        // 1. Блокування сигналів для обробки через signalfd
        sigset_t mask;
        sigemptyset(&mask);
        sigaddset(&mask, SIGINT);
        sigaddset(&mask, SIGTERM);
        sigprocmask(SIG_BLOCK, &mask, nullptr);

        signal_fd_.reset(::signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC));
        if (!signal_fd_) throw std::system_error(errno, std::generic_category(), "signalfd");

        // 2. Створення неблокуючого TCP-сокета
        listen_fd_.reset(::socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0));
        if (!listen_fd_) throw std::system_error(errno, std::generic_category(), "socket");

        int opt = 1;
        ::setsockopt(listen_fd_.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        sockaddr_in srv_addr{};
        srv_addr.sin_family = AF_INET;
        srv_addr.sin_addr.s_addr = INADDR_ANY;
        srv_addr.sin_port = htons(Port);

        if (::bind(listen_fd_.get(), reinterpret_cast<sockaddr*>(&srv_addr), sizeof(srv_addr)) == -1) {
            throw std::system_error(errno, std::generic_category(), "bind");
        }
        if (::listen(listen_fd_.get(), SOMAXCONN) == -1) {
            throw std::system_error(errno, std::generic_category(), "listen");
        }

        // 3. Таймер перевірки неактивних сесій (раз на 5 с)
        timer_fd_.reset(::timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC));
        itimerspec ts{};
        ts.it_interval.tv_sec = 5;
        ts.it_value.tv_sec = 5;
        ::timerfd_settime(timer_fd_.get(), 0, &ts, nullptr);

        // 4. Створення epoll
        epfd_.reset(::epoll_create1(EPOLL_CLOEXEC));
        if (!epfd_) throw std::system_error(errno, std::generic_category(), "epoll_create1");

        add_event(listen_fd_.get(), EPOLLIN | EPOLLET, nullptr);
        add_event(signal_fd_.get(), EPOLLIN, nullptr);
        add_event(timer_fd_.get(), EPOLLIN, nullptr);
    }

    void run() {
        running_ = true;
        std::cout << "C++ Reactor сервер запущено на порту " << Port << "...\n";

        std::vector<epoll_event> events(MaxEvents);

        while (running_) {
            int nready = ::epoll_wait(epfd_.get(), events.data(), MaxEvents, -1);
            if (nready == -1) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "epoll_wait");
            }

            for (int i = 0; i < nready; ++i) {
                const auto& ev = events[i];

                if (ev.data.fd == signal_fd_.get()) {
                    handle_signals();
                    break;
                }
                if (ev.data.fd == timer_fd_.get()) {
                    handle_timer();
                    continue;
                }
                if (ev.data.fd == listen_fd_.get()) {
                    handle_accept();
                    continue;
                }

                auto* session = static_cast<Session*>(ev.data.ptr);
                if (!session) continue;

                int client_fd = session->socket.get();
                if (ev.events & (EPOLLERR | EPOLLHUP | EPOLLRDHUP)) {
                    close_session(client_fd);
                    continue;
                }
                if (ev.events & EPOLLIN) {
                    handle_read(*session);
                }
                if (sessions_.contains(client_fd) && (ev.events & EPOLLOUT)) {
                    handle_write(*session);
                }
            }
        }
        std::cout << "C++ Reactor сервер зупинено.\n";
    }

private:
    void add_event(int fd, uint32_t event_mask, void* ptr) {
        epoll_event ev{};
        ev.events = event_mask;
        if (ptr) {
            ev.data.ptr = ptr;
        } else {
            ev.data.fd = fd;
        }
        if (::epoll_ctl(epfd_.get(), EPOLL_CTL_ADD, fd, &ev) == -1) {
            throw std::system_error(errno, std::generic_category(), "epoll_ctl ADD");
        }
    }

    void mod_event(int fd, uint32_t event_mask, void* ptr) {
        epoll_event ev{};
        ev.events = event_mask;
        ev.data.ptr = ptr;
        ::epoll_ctl(epfd_.get(), EPOLL_CTL_MOD, fd, &ev);
    }

    void handle_accept() {
        while (true) {
            sockaddr_in client_addr{};
            socklen_t client_len = sizeof(client_addr);
            int client_raw = ::accept4(listen_fd_.get(), 
                                       reinterpret_cast<sockaddr*>(&client_addr),
                                       &client_len, SOCK_NONBLOCK | SOCK_CLOEXEC);
            if (client_raw == -1) {
                if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                break;
            }

            auto session = std::make_unique<Session>(UniqueFd(client_raw));
            int fd = session->socket.get();
            Session* session_ptr = session.get();

            sessions_[fd] = std::move(session);
            add_event(fd, EPOLLIN | EPOLLET | EPOLLRDHUP, session_ptr);

            char ip_str[INET_ADDRSTRLEN];
            ::inet_ntop(AF_INET, &client_addr.sin_addr, ip_str, sizeof(ip_str));
            std::cout << "[CONNECT] Клієнт FD " << fd << " з " << ip_str << "\n";
        }
    }

    void handle_read(Session& session) {
        char buf[BufferSize];
        session.last_active = std::chrono::steady_clock::now();
        int fd = session.socket.get();

        while (true) {
            ssize_t n = ::read(fd, buf, sizeof(buf));
            if (n > 0) {
                session.out_buffer.insert(session.out_buffer.end(), buf, buf + n);
            } else if (n == 0) {
                close_session(fd);
                return;
            } else {
                if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                close_session(fd);
                return;
            }
        }

        if (!session.out_buffer.empty()) {
            flush_write(session);
        }
    }

    void handle_write(Session& session) {
        flush_write(session);
    }

    void flush_write(Session& session) {
        int fd = session.socket.get();
        session.last_active = std::chrono::steady_clock::now();

        while (!session.out_buffer.empty()) {
            ssize_t n = ::write(fd, session.out_buffer.data(), session.out_buffer.size());
            if (n > 0) {
                session.out_buffer.erase(session.out_buffer.begin(), session.out_buffer.begin() + n);
            } else if (n == -1) {
                if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                close_session(fd);
                return;
            }
        }

        uint32_t mask = EPOLLIN | EPOLLET | EPOLLRDHUP;
        if (!session.out_buffer.empty()) {
            mask |= EPOLLOUT;
        }
        mod_event(fd, mask, &session);
    }

    void handle_signals() {
        signalfd_siginfo fdsi{};
        ::read(signal_fd_.get(), &fdsi, sizeof(fdsi));
        std::cout << "\n[SIGNAL] Сигнал " << fdsi.ssi_signo << ". Завершення...\n";
        running_ = false;
    }

    void handle_timer() {
        uint64_t exp = 0;
        ::read(timer_fd_.get(), &exp, sizeof(exp));
    }

    void close_session(int fd) {
        ::epoll_ctl(epfd_.get(), EPOLL_CTL_DEL, fd, nullptr);
        sessions_.erase(fd);
        std::cout << "[DISCONNECT] Клієнт FD " << fd << " видалений\n";
    }
};

} // namespace net

int main() {
    try {
        net::ReactorServer server;
        server.init();
        server.run();
    } catch (const std::exception& ex) {
        std::cerr << "Fatal error: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
