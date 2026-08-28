#include <sys/types.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <sys/signalfd.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <csignal>
#include <cstdlib>
#include <cstring>
#include <string_view>
#include <iostream>
#include <vector>
#include <expected>
#include <system_error>

namespace production {

constexpr int max_events = 64;
constexpr int buffer_size = 4096;
constexpr int default_port = 8080;
constexpr int sd_listen_fds_start = 3;

// RAII обгортка для надійного володіння файловим дескриптором Linux
class unique_fd {
    int m_fd = -1;
public:
    explicit unique_fd(int fd = -1) noexcept : m_fd(fd) {}
    ~unique_fd() noexcept { if (m_fd >= 0) ::close(m_fd); }

    unique_fd(const unique_fd&) = delete;
    unique_fd& operator=(const unique_fd&) = delete;

    unique_fd(unique_fd&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    unique_fd& operator=(unique_fd&& other) noexcept {
        if (this != &other) {
            if (m_fd >= 0) ::close(m_fd);
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }
    void reset(int fd = -1) noexcept {
        if (m_fd >= 0) ::close(m_fd);
        m_fd = fd;
    }
    int release() noexcept {
        int fd = m_fd;
        m_fd = -1;
        return fd;
    }
};

// Відправка повідомлень у systemd через NOTIFY_SOCKET
void notify_systemd(std::string_view state) noexcept {
    const char* sock_path = std::getenv("NOTIFY_SOCKET");
    if (!sock_path || state.empty()) return;

    struct sockaddr_un addr{};
    addr.sun_family = AF_UNIX;

    const size_t len = std::strlen(sock_path);
    if (len >= sizeof(addr.sun_path)) return;

    if (sock_path[0] == '@') {
        addr.sun_path[0] = '\0';
        std::memcpy(&addr.sun_path[1], &sock_path[1], len - 1);
    } else {
        std::memcpy(addr.sun_path, sock_path, len);
    }

    int fd = ::socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (fd < 0) return;

    auto addr_len = static_cast<socklen_t>(offsetof(struct sockaddr_un, sun_path) + len);
    ::sendto(fd, state.data(), state.size(), MSG_NOSIGNAL,
             reinterpret_cast<struct sockaddr*>(&addr), addr_len);
    ::close(fd);
}

// Отримання або створення сокета прослуховування
[[nodiscard]] std::expected<unique_fd, std::error_code> create_listen_socket(int port) noexcept {
    const char* listen_pid_str = std::getenv("LISTEN_PID");
    const char* listen_fds_str = std::getenv("LISTEN_FDS");

    if (listen_pid_str && listen_fds_str) {
        pid_t pid = std::atoi(listen_pid_str);
        int count = std::atoi(listen_fds_str);
        if (pid == ::getpid() && count > 0) {
            std::cout << "<6>Використано сокет від systemd (socket activation)\n";
            int flags = ::fcntl(sd_listen_fds_start, F_GETFL, 0);
            ::fcntl(sd_listen_fds_start, F_SETFL, flags | O_NONBLOCK);
            return unique_fd(sd_listen_fds_start);
        }
    }

    int fd = ::socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    unique_fd sock(fd);

    int opt = 1;
    ::setsockopt(sock.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(static_cast<uint16_t>(port));

    if (::bind(sock.get(), reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (::listen(sock.get(), SOMAXCONN) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    std::cout << "<6>Слухаємо порт " << port << '\n';
    return sock;
}

} // namespace production

int main(int argc, char* argv[]) {
    int port = production::default_port;
    if (argc > 1) {
        port = std::atoi(argv[1]);
    }

    ::signal(SIGPIPE, SIG_IGN);

    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGTERM);
    sigaddset(&mask, SIGINT);
    sigaddset(&mask, SIGHUP);

    if (::sigprocmask(SIG_BLOCK, &mask, nullptr) < 0) {
        std::cerr << "<3>Помилка виклику sigprocmask\n";
        return EXIT_FAILURE;
    }

    production::unique_fd sfd(::signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC));
    if (!sfd.valid()) {
        std::cerr << "<3>Помилка створення signalfd\n";
        return EXIT_FAILURE;
    }

    production::unique_fd epoll_fd(::epoll_create1(EPOLL_CLOEXEC));
    if (!epoll_fd.valid()) {
        std::cerr << "<3>Помилка виклику epoll_create1\n";
        return EXIT_FAILURE;
    }

    struct epoll_event ev{};
    ev.events = EPOLLIN;
    ev.data.fd = sfd.get();
    ::epoll_ctl(epoll_fd.get(), EPOLL_CTL_ADD, sfd.get(), &ev);

    auto listen_sock_res = production::create_listen_socket(port);
    if (!listen_sock_res) {
        std::cerr << "<3>Помилка створення слухаючого сокета: " 
                  << listen_sock_res.error().message() << '\n';
        return EXIT_FAILURE;
    }
    production::unique_fd listen_sock = std::move(*listen_sock_res);

    ev.events = EPOLLIN;
    ev.data.fd = listen_sock.get();
    ::epoll_ctl(epoll_fd.get(), EPOLL_CTL_ADD, listen_sock.get(), &ev);

    production::notify_systemd("READY=1\nSTATUS=C++23 Сервер готовий до роботи");

    std::vector<struct epoll_event> events(production::max_events);
    bool running = true;
    int active_connections = 0;

    std::cout << "<6>Головний цикл подій C++ успішно запущено\n";

    while (running || active_connections > 0) {
        int timeout = running ? 5000 : 1000;
        int nfds = ::epoll_wait(epoll_fd.get(), events.data(), production::max_events, timeout);

        if (nfds < 0) {
            if (errno == EINTR) continue;
            std::cerr << "<3>Помилка epoll_wait: " << std::strerror(errno) << '\n';
            break;
        }

        if (nfds == 0 && running) {
            production::notify_systemd("WATCHDOG=1");
            continue;
        }

        for (int i = 0; i < nfds; ++i) {
            int cur_fd = events[i].data.fd;

            if (cur_fd == sfd.get()) {
                struct signalfd_siginfo fdsi{};
                if (::read(sfd.get(), &fdsi, sizeof(fdsi)) == sizeof(fdsi)) {
                    if (fdsi.ssi_signo == SIGTERM || fdsi.ssi_signo == SIGINT) {
                        std::cout << "<5>Отримано сигнал зупинки. Початок Graceful Shutdown...\n";
                        production::notify_systemd("STOPPING=1\nSTATUS=Завершення роботи");
                        running = false;
                        ::epoll_ctl(epoll_fd.get(), EPOLL_CTL_DEL, listen_sock.get(), nullptr);
                        listen_sock.reset();
                    } else if (fdsi.ssi_signo == SIGHUP) {
                        std::cout << "<6>Отримано SIGHUP: перезавантаження конфігурації\n";
                        production::notify_systemd("RELOADING=1");
                        production::notify_systemd("READY=1\nSTATUS=Конфігурацію оновлено");
                    }
                }
            } else if (listen_sock.valid() && cur_fd == listen_sock.get()) {
                while (true) {
                    struct sockaddr_in client_addr{};
                    socklen_t client_len = sizeof(client_addr);
                    int client_fd = ::accept4(listen_sock.get(),
                                              reinterpret_cast<struct sockaddr*>(&client_addr),
                                              &client_len, SOCK_NONBLOCK | SOCK_CLOEXEC);
                    if (client_fd < 0) {
                        if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                        break;
                    }

                    ev.events = EPOLLIN | EPOLLRDHUP;
                    ev.data.fd = client_fd;
                    ::epoll_ctl(epoll_fd.get(), EPOLL_CTL_ADD, client_fd, &ev);
                    active_connections++;
                }
            } else {
                std::vector<char> buffer(production::buffer_size);
                ssize_t count = ::read(cur_fd, buffer.data(), buffer.size());

                if (count > 0) {
                    ::send(cur_fd, buffer.data(), static_cast<size_t>(count), MSG_NOSIGNAL);
                } else if (count == 0 || (count < 0 && errno != EAGAIN)) {
                    ::epoll_ctl(epoll_fd.get(), EPOLL_CTL_DEL, cur_fd, nullptr);
                    ::close(cur_fd);
                    active_connections--;
                }
            }
        }
    }

    std::cout << "<6>Усі сесії завершено. Процес виходить штатно.\n";
    return EXIT_SUCCESS;
}
