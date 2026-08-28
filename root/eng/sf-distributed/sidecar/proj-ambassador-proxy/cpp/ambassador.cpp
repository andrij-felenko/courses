// ambassador.cpp — Ідіоматичний об'єктно-орієнтований Ambassador-проксі на C++20
#include <iostream>
#include <string>
#include <vector>
#include <span>
#include <chrono>
#include <random>
#include <thread>
#include <memory>
#include <atomic>
#include <expected>
#include <system_error>
#include <cstring>
#include <csignal>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>

using namespace std::chrono_literals;

namespace ambassador {

// RAII обгортка для безпечного володіння файловим дескриптором сокета
class SocketHandle {
    int fd_{-1};
public:
    explicit SocketHandle(int fd = -1) noexcept : fd_(fd) {}
    ~SocketHandle() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;
    SocketHandle(SocketHandle&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    SocketHandle& operator=(SocketHandle&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    void reset(int fd = -1) noexcept {
        if (fd_ >= 0) ::close(fd_);
        fd_ = fd;
    }
};

enum class CircuitState { Closed, Open, HalfOpen };

class CircuitBreaker {
    CircuitState state_{CircuitState::Closed};
    int failure_count_{0};
    const int threshold_{5};
    const std::chrono::seconds recovery_timeout_{10s};
    std::chrono::steady_clock::time_point last_state_change_{std::chrono::steady_clock::now()};

public:
    explicit CircuitBreaker(int threshold = 5) : threshold_(threshold) {}

    bool allow_request() {
        auto now = std::chrono::steady_clock::now();
        if (state_ == CircuitState::Open) {
            if (now - last_state_change_ >= recovery_timeout_) {
                state_ = CircuitState::HalfOpen;
                last_state_change_ = now;
                return true;
            }
            return false;
        }
        return true;
    }

    void record_success() noexcept {
        failure_count_ = 0;
        state_ = CircuitState::Closed;
    }

    void record_failure() noexcept {
        ++failure_count_;
        if (failure_count_ >= threshold_ || state_ == CircuitState::HalfOpen) {
            state_ = CircuitState::Open;
            last_state_change_ = std::chrono::steady_clock::now();
        }
    }

    [[nodiscard]] CircuitState state() const noexcept { return state_; }
};

class ProxyEngine {
    std::string upstream_ip_;
    int upstream_port_;
    CircuitBreaker cb_;
    std::mt19937 rng_{std::random_device{}()};

    std::expected<SocketHandle, std::error_code> connect_upstream() {
        int raw_fd = ::socket(AF_INET, SOCK_STREAM, 0);
        if (raw_fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        SocketHandle sock(raw_fd);

        int flag = 1;
        ::setsockopt(sock.get(), IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));

        timeval tv{ .tv_sec = 2, .tv_usec = 0 };
        ::setsockopt(sock.get(), SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
        ::setsockopt(sock.get(), SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(upstream_port_);
        ::inet_pton(AF_INET, upstream_ip_.c_str(), &addr.sin_addr);

        if (::connect(sock.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return sock;
    }

    void sleep_with_jitter(std::chrono::milliseconds base_ms) {
        std::uniform_int_distribution<int> dist(0, 20);
        std::this_thread::sleep_for(base_ms + std::chrono::milliseconds(dist(rng_)));
    }

public:
    ProxyEngine(std::string ip, int port)
        : upstream_ip_(std::move(ip)), upstream_port_(port) {}

    void handle_client(SocketHandle client) {
        std::vector<char> buffer(8192);
        ssize_t n_read = ::read(client.get(), buffer.data(), buffer.size());
        if (n_read <= 0) return;

        if (!cb_.allow_request()) {
            std::string_view err = "HTTP/1.1 503 Service Unavailable (Circuit Breaker Open)\r\nContent-Length: 0\r\n\r\n";
            ::write(client.get(), err.data(), err.size());
            return;
        }

        constexpr int max_retries = 3;
        bool success = false;

        for (int attempt = 1; attempt <= max_retries && !success; ++attempt) {
            auto up_res = connect_upstream();
            if (up_res) {
                SocketHandle upstream = std::move(*up_res);
                if (::write(upstream.get(), buffer.data(), n_read) == n_read) {
                    ssize_t up_read = ::read(upstream.get(), buffer.data(), buffer.size());
                    if (up_read > 0) {
                        ::write(client.get(), buffer.data(), up_read);
                        success = true;
                    }
                }
            }

            if (!success && attempt < max_retries) {
                sleep_with_jitter(std::chrono::milliseconds(50 * (1 << attempt)));
            }
        }

        if (success) {
            cb_.record_success();
        } else {
            cb_.record_failure();
            std::string_view err = "HTTP/1.1 504 Gateway Timeout (Upstream Failed)\r\nContent-Length: 0\r\n\r\n";
            ::write(client.get(), err.data(), err.size());
        }
    }
};

} // namespace ambassador

static std::atomic<bool> g_stop{false};
static void on_signal(int) { g_stop.store(true); }

int main() {
    std::signal(SIGTERM, on_signal);
    std::signal(SIGINT, on_signal);
    std::signal(SIGPIPE, SIG_IGN);

    int raw_listen = ::socket(AF_INET, SOCK_STREAM, 0);
    if (raw_listen < 0) return 1;
    ambassador::SocketHandle listener(raw_listen);

    int opt = 1;
    ::setsockopt(listener.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in laddr{};
    laddr.sin_family = AF_INET;
    laddr.sin_port = htons(8081);
    ::inet_pton(AF_INET, "127.0.0.1", &laddr.sin_addr);

    if (::bind(listener.get(), reinterpret_cast<sockaddr*>(&laddr), sizeof(laddr)) < 0) return 1;
    if (::listen(listener.get(), 128) < 0) return 1;

    ambassador::ProxyEngine engine("127.0.0.1", 9000);
    std::cout << "[Ambassador-C++] Сервер слухає 127.0.0.1:8081 -> 127.0.0.1:9000\n";

    while (!g_stop.load()) {
        sockaddr_in caddr{};
        socklen_t clen = sizeof(caddr);
        int client_fd = ::accept(listener.get(), reinterpret_cast<sockaddr*>(&caddr), &clen);
        if (client_fd < 0) {
            if (errno == EINTR) break;
            continue;
        }
        engine.handle_client(ambassador::SocketHandle(client_fd));
    }

    std::cout << "[Ambassador-C++] Коректне завершення роботи.\n";
    return 0;
}
