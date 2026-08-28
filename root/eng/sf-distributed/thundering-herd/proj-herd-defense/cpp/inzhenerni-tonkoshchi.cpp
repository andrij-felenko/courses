// C++20 implementation: modern RAII connection manager with Decorrelated Jitter
#include <iostream>
#include <chrono>
#include <random>
#include <thread>
#include <expected>
#include <system_error>
#include <string_view>
#include <cstring>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

class SocketHandle {
public:
    explicit SocketHandle(int fd = -1) noexcept : fd_(fd) {}
    ~SocketHandle() { reset(); }

    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;

    SocketHandle(SocketHandle&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    SocketHandle& operator=(SocketHandle&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

    int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

private:
    int fd_{-1};
};

class DecorrelatedJitterBackoff {
public:
    DecorrelatedJitterBackoff(std::chrono::milliseconds base,
                              std::chrono::milliseconds max)
        : base_(base), max_(max), prev_(base),
          rng_(std::random_device{}()) {}

    std::chrono::milliseconds next() {
        const auto low = base_.count();
        const auto high = std::max(low, prev_.count() * 3);
        
        std::uniform_int_distribution<long long> dist(low, high);
        const auto sleep_ms = std::min(max_.count(), dist(rng_));
        
        prev_ = std::chrono::milliseconds(sleep_ms);
        return prev_;
    }

private:
    std::chrono::milliseconds base_;
    std::chrono::milliseconds max_;
    std::chrono::milliseconds prev_;
    std::mt19937_64 rng_;
};

class ResilientClient {
public:
    ResilientClient(std::string_view host, int port)
        : host_(host), port_(port),
          backoff_(std::chrono::milliseconds(500), std::chrono::seconds(30)) {}

    std::expected<SocketHandle, std::error_code> connect(int max_attempts) {
        struct sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port_);
        if (::inet_pton(AF_INET, host_.data(), &addr.sin_addr) <= 0) {
            return std::unexpected(std::make_error_code(std::errc::invalid_argument));
        }

        for (int attempt = 1; attempt <= max_attempts; ++attempt) {
            SocketHandle sock(::socket(AF_INET, SOCK_STREAM, 0));
            if (!sock.valid()) {
                return std::unexpected(std::make_error_code(std::errc::bad_file_descriptor));
            }

            if (::connect(sock.get(), reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) == 0) {
                std::cout << "[Client C++] Connected successfully on attempt " << attempt << "\n";
                return sock;
            }

            const auto delay = backoff_.next();
            std::cout << "[Client C++] Attempt " << attempt << " failed. Sleeping "
                      << delay.count() << " ms\n";
            std::this_thread::sleep_for(delay);
        }

        return std::unexpected(std::make_error_code(std::errc::timed_out));
    }

private:
    std::string_view host_;
    int port_;
    DecorrelatedJitterBackoff backoff_;
};
