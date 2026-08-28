#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <unordered_map>
#include <span>
#include <expected>
#include <system_error>
#include <csignal>

#include <unistd.h>
#include <fcntl.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

namespace proxy {

// RAII обгортка для автоматичного керування життєвим циклом файлового дескриптора
class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
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
    int fd_{-1};
};

enum class SessionState {
    ConnectingUpstream,
    Streaming
};

struct Session {
    UniqueFd client_fd;
    UniqueFd upstream_fd;
    SessionState state{SessionState::ConnectingUpstream};
    std::string client_ip;
};

class ReverseProxyEngine {
public:
    static constexpr int MaxEvents = 1024;
    static constexpr size_t BufferSize = 16384;

    ReverseProxyEngine(std::string upstream_host, uint16_t upstream_port)
        : upstream_host_(std::move(upstream_host)), upstream_port_(upstream_port) {}

    std::expected<void, std::error_code> run(uint16_t listen_port) {
        ::signal(SIGPIPE, SIG_IGN);

        auto listen_res = create_listener(listen_port);
        if (!listen_res) return std::unexpected(listen_res.error());
        listen_fd_ = std::move(*listen_res);

        int ep_fd = ::epoll_create1(0);
        if (ep_fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        epoll_fd_.reset(ep_fd);

        epoll_event ev{};
        ev.events = EPOLLIN;
        ev.data.fd = listen_fd_.get();
        if (::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_ADD, listen_fd_.get(), &ev) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        std::vector<epoll_event> events(MaxEvents);
        std::vector<uint8_t> io_buffer(BufferSize);

        std::cout << "Зворотний проксі (C++20) запущено на порту " << listen_port
                  << " -> " << upstream_host_ << ":" << upstream_port_ << '\n';

        while (true) {
            int n_ready = ::epoll_wait(epoll_fd_.get(), events.data(), MaxEvents, -1);
            if (n_ready < 0) {
                if (errno == EINTR) continue;
                break;
            }

            for (int i = 0; i < n_ready; ++i) {
                const auto& event = events[i];

                if (event.data.fd == listen_fd_.get()) {
                    accept_clients();
                } else {
                    int fd = event.data.fd;
                    auto it = sessions_by_fd_.find(fd);
                    if (it == sessions_by_fd_.end()) continue;

                    auto session = it->second;
                    if (event.events & (EPOLLRDHUP | EPOLLERR | EPOLLHUP)) {
                        remove_session(session);
                        continue;
                    }

                    handle_io(session, io_buffer);
                }
            }
        }
        return {};
    }

private:
    static std::expected<void, std::error_code> make_non_blocking(int fd) {
        int flags = ::fcntl(fd, F_GETFL, 0);
        if (flags < 0 || ::fcntl(fd, F_SETFL, flags | O_NONBLOCK) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }

    std::expected<UniqueFd, std::error_code> create_listener(uint16_t port) {
        UniqueFd fd(::socket(AF_INET, SOCK_STREAM, 0));
        if (!fd.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        int opt = 1;
        ::setsockopt(fd.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
        if (auto res = make_non_blocking(fd.get()); !res) return std::unexpected(res.error());

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = htonl(INADDR_ANY);
        addr.sin_port = htons(port);

        if (::bind(fd.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0 ||
            ::listen(fd.get(), SOMAXCONN) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return fd;
    }

    std::expected<UniqueFd, std::error_code> connect_upstream() {
        UniqueFd fd(::socket(AF_INET, SOCK_STREAM, 0));
        if (!fd.valid()) return std::unexpected(std::error_code(errno, std::generic_category()));
        if (auto res = make_non_blocking(fd.get()); !res) return std::unexpected(res.error());

        sockaddr_in up_addr{};
        up_addr.sin_family = AF_INET;
        up_addr.sin_port = htons(upstream_port_);
        ::inet_pton(AF_INET, upstream_host_.c_str(), &up_addr.sin_addr);

        int res = ::connect(fd.get(), reinterpret_cast<sockaddr*>(&up_addr), sizeof(up_addr));
        if (res < 0 && errno != EINPROGRESS) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return fd;
    }

    void accept_clients() {
        while (true) {
            sockaddr_in c_addr{};
            socklen_t c_len = sizeof(c_addr);
            int c_fd = ::accept(listen_fd_.get(), reinterpret_cast<sockaddr*>(&c_addr), &c_len);
            if (c_fd < 0) {
                if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                break;
            }

            make_non_blocking(c_fd);
            auto up_res = connect_upstream();
            if (!up_res) {
                ::close(c_fd);
                continue;
            }

            char ip_buf[INET_ADDRSTRLEN]{};
            ::inet_ntop(AF_INET, &c_addr.sin_addr, ip_buf, sizeof(ip_buf));

            auto session = std::make_shared<Session>();
            session->client_fd.reset(c_fd);
            session->upstream_fd = std::move(*up_res);
            session->state = SessionState::ConnectingUpstream;
            session->client_ip = ip_buf;

            int client_raw = session->client_fd.get();
            int up_raw = session->upstream_fd.get();

            sessions_by_fd_[client_raw] = session;
            sessions_by_fd_[up_raw] = session;

            epoll_event ev_c{};
            ev_c.events = EPOLLIN | EPOLLRDHUP | EPOLLERR;
            ev_c.data.fd = client_raw;
            ::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_ADD, client_raw, &ev_c);

            epoll_event ev_u{};
            ev_u.events = EPOLLOUT | EPOLLRDHUP | EPOLLERR;
            ev_u.data.fd = up_raw;
            ::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_ADD, up_raw, &ev_u);
        }
    }

    void handle_io(const std::shared_ptr<Session>& session, std::span<uint8_t> buffer) {
        if (session->state == SessionState::ConnectingUpstream) {
            int err = 0;
            socklen_t len = sizeof(err);
            if (::getsockopt(session->upstream_fd.get(), SOL_SOCKET, SO_ERROR, &err, &len) < 0 || err != 0) {
                remove_session(session);
                return;
            }
            session->state = SessionState::Streaming;

            epoll_event ev_u{};
            ev_u.events = EPOLLIN | EPOLLRDHUP | EPOLLERR;
            ev_u.data.fd = session->upstream_fd.get();
            ::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_MOD, session->upstream_fd.get(), &ev_u);
        }

        // Передача від клієнта до апстріму
        ssize_t n_client = ::read(session->client_fd.get(), buffer.data(), buffer.size());
        if (n_client > 0) {
            ::write(session->upstream_fd.get(), buffer.data(), static_cast<size_t>(n_client));
        } else if (n_client == 0 || (n_client < 0 && errno != EAGAIN)) {
            remove_session(session);
            return;
        }

        // Передача від апстріму до клієнта
        ssize_t n_up = ::read(session->upstream_fd.get(), buffer.data(), buffer.size());
        if (n_up > 0) {
            ::write(session->client_fd.get(), buffer.data(), static_cast<size_t>(n_up));
        } else if (n_up == 0 || (n_up < 0 && errno != EAGAIN)) {
            remove_session(session);
            return;
        }
    }

    void remove_session(const std::shared_ptr<Session>& session) {
        if (!session) return;
        if (session->client_fd.valid()) {
            ::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_DEL, session->client_fd.get(), nullptr);
            sessions_by_fd_.erase(session->client_fd.get());
        }
        if (session->upstream_fd.valid()) {
            ::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_DEL, session->upstream_fd.get(), nullptr);
            sessions_by_fd_.erase(session->upstream_fd.get());
        }
    }

    std::string upstream_host_;
    uint16_t upstream_port_;
    UniqueFd listen_fd_;
    UniqueFd epoll_fd_;
    std::unordered_map<int, std::shared_ptr<Session>> sessions_by_fd_;
};

} // namespace proxy

int main() {
    proxy::ReverseProxyEngine engine("127.0.0.1", 8000);
    auto res = engine.run(8080);
    if (!res) {
        std::cerr << "Помилка роботи проксі: " << res.error().message() << '\n';
        return 1;
    }
    return 0;
}
