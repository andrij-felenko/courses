#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <chrono>
#include <atomic>
#include <algorithm>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>

class SocketHandle {
    int fd_{-1};
public:
    explicit SocketHandle(int fd = -1) noexcept : fd_(fd) {}
    ~SocketHandle() { reset(); }

    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;

    SocketHandle(SocketHandle&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
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

    int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

    void set_nonblocking() {
        if (fd_ < 0) return;
        int flags = ::fcntl(fd_, F_GETFL, 0);
        if (flags >= 0) {
            ::fcntl(fd_, F_SETFL, flags | O_NONBLOCK);
        }
    }
};

struct BackendEndpoint {
    std::string ip;
    int port;
    std::atomic<int> active_requests{0};
    std::atomic<bool> is_healthy{true};
    std::atomic<int> consecutive_failures{0};
    std::atomic<int> consecutive_successes{3};
};

class LoadBalancer {
    std::vector<std::shared_ptr<BackendEndpoint>> backends_;
    std::atomic<size_t> round_robin_counter_{0};

public:
    void add_backend(std::string ip, int port) {
        auto endpoint = std::make_shared<BackendEndpoint>();
        endpoint->ip = std::move(ip);
        endpoint->port = port;
        backends_.push_back(std::move(endpoint));
    }

    [[nodiscard]] std::shared_ptr<BackendEndpoint> select_least_connections() {
        std::shared_ptr<BackendEndpoint> best = nullptr;
        int min_conns = 1000000;

        for (const auto& backend : backends_) {
            if (!backend->is_healthy.load(std::memory_order_relaxed)) {
                continue;
            }
            int current = backend->active_requests.load(std::memory_order_relaxed);
            if (current < min_conns) {
                min_conns = current;
                best = backend;
            }
        }
        return best;
    }

    [[nodiscard]] std::shared_ptr<BackendEndpoint> select_power_of_two() {
        if (backends_.empty()) return nullptr;
        if (backends_.size() == 1) return backends_.front();

        size_t idx1 = rand() % backends_.size();
        size_t idx2 = rand() % backends_.size();
        while (idx2 == idx1 && backends_.size() > 1) {
            idx2 = rand() % backends_.size();
        }

        auto& b1 = backends_[idx1];
        auto& b2 = backends_[idx2];

        bool h1 = b1->is_healthy.load(std::memory_order_relaxed);
        bool h2 = b2->is_healthy.load(std::memory_order_relaxed);

        if (h1 && !h2) return b1;
        if (!h1 && h2) return b2;
        if (!h1 && !h2) return nullptr;

        return (b1->active_requests.load(std::memory_order_relaxed) <=
                b2->active_requests.load(std::memory_order_relaxed)) ? b1 : b2;
    }

    void perform_health_checks() {
        for (auto& backend : backends_) {
            SocketHandle sock(::socket(AF_INET, SOCK_STREAM, 0));
            if (!sock.valid()) continue;

            struct timeval tv{ .tv_sec = 1, .tv_usec = 0 };
            ::setsockopt(sock.get(), SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
            ::setsockopt(sock.get(), SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));

            sockaddr_in addr{};
            addr.sin_family = AF_INET;
            addr.sin_port = htons(backend->port);
            ::inet_pton(AF_INET, backend->ip.c_str(), &addr.sin_addr);

            bool success = false;
            if (::connect(sock.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == 0) {
                std::string_view req = "GET /healthz HTTP/1.1\r\nHost: probe\r\nConnection: close\r\n\r\n";
                if (::write(sock.get(), req.data(), req.size()) == static_cast<ssize_t>(req.size())) {
                    char buf[128];
                    ssize_t n = ::read(sock.get(), buf, sizeof(buf) - 1);
                    if (n > 0) {
                        buf[n] = '\0';
                        if (std::string_view(buf).find("200 OK") != std::string_view::npos) {
                            success = true;
                        }
                    }
                }
            }

            if (success) {
                backend->consecutive_failures.store(0, std::memory_order_relaxed);
                int ok_count = ++backend->consecutive_successes;
                if (ok_count >= 2) {
                    backend->is_healthy.store(true, std::memory_order_relaxed);
                }
            } else {
                backend->consecutive_successes.store(0, std::memory_order_relaxed);
                int fail_count = ++backend->consecutive_failures;
                if (fail_count >= 3) {
                    backend->is_healthy.store(false, std::memory_order_relaxed);
                }
            }
        }
    }
};

class AsyncReverseProxy {
    SocketHandle listen_sock_;
    SocketHandle epoll_fd_;
    LoadBalancer balancer_;
    static constexpr size_t BufferSize = 16384;

public:
    AsyncReverseProxy(int port) {
        listen_sock_.reset(::socket(AF_INET, SOCK_STREAM, 0));
        if (!listen_sock_.valid()) throw std::system_error(errno, std::generic_category());

        int opt = 1;
        ::setsockopt(listen_sock_.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
        listen_sock_.set_nonblocking();

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(port);

        if (::bind(listen_sock_.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            throw std::system_error(errno, std::generic_category());
        }
        if (::listen(listen_sock_.get(), 1024) < 0) {
            throw std::system_error(errno, std::generic_category());
        }

        epoll_fd_.reset(::epoll_create1(0));
        if (!epoll_fd_.valid()) throw std::system_error(errno, std::generic_category());

        epoll_event ev{};
        ev.events = EPOLLIN;
        ev.data.fd = listen_sock_.get();
        ::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_ADD, listen_sock_.get(), &ev);
    }

    void add_upstream(std::string ip, int port) {
        balancer_.add_backend(std::move(ip), port);
    }

    void run() {
        constexpr int MaxEvents = 64;
        epoll_event events[MaxEvents];
        auto last_health_check = std::chrono::steady_clock::now();

        while (true) {
            auto now = std::chrono::steady_clock::now();
            if (std::chrono::duration_cast<std::chrono::seconds>(now - last_health_check).count() >= 5) {
                balancer_.perform_health_checks();
                last_health_check = now;
            }

            int nfds = ::epoll_wait(epoll_fd_.get(), events, MaxEvents, 1000);
            for (int i = 0; i < nfds; ++i) {
                if (events[i].data.fd == listen_sock_.get()) {
                    sockaddr_in client_addr{};
                    socklen_t len = sizeof(client_addr);
                    int client_raw = ::accept(listen_sock_.get(), reinterpret_cast<sockaddr*>(&client_addr), &len);
                    if (client_raw >= 0) {
                        SocketHandle client(client_raw);
                        client.set_nonblocking();

                        auto backend = balancer_.select_least_connections();
                        if (!backend) {
                            std::string_view err = "HTTP/1.1 503 Service Unavailable\r\nContent-Length: 21\r\n\r\nNo Healthy Backends\n";
                            ::write(client.get(), err.data(), err.size());
                            continue;
                        }

                        SocketHandle backend_sock(::socket(AF_INET, SOCK_STREAM, 0));
                        sockaddr_in b_addr{};
                        b_addr.sin_family = AF_INET;
                        b_addr.sin_port = htons(backend->port);
                        ::inet_pton(AF_INET, backend->ip.c_str(), &b_addr.sin_addr);

                        backend->active_requests.fetch_add(1, std::memory_order_relaxed);
                        if (::connect(backend_sock.get(), reinterpret_cast<sockaddr*>(&b_addr), sizeof(b_addr)) == 0) {
                            std::vector<char> buf(BufferSize);
                            ssize_t r = ::read(client.get(), buf.data(), buf.size());
                            if (r > 0) {
                                ::write(backend_sock.get(), buf.data(), r);
                                ssize_t resp_len = ::read(backend_sock.get(), buf.data(), buf.size());
                                if (resp_len > 0) {
                                    ::write(client.get(), buf.data(), resp_len);
                                }
                            }
                        }
                        backend->active_requests.fetch_sub(1, std::memory_order_relaxed);
                    }
                }
            }
        }
    }
};

int main(int argc, char* argv[]) {
    int port = (argc > 1) ? std::stoi(argv[1]) : 8080;
    try {
        AsyncReverseProxy proxy(port);
        proxy.add_upstream("127.0.0.1", 8081);
        proxy.add_upstream("127.0.0.1", 8082);
        proxy.run();
    } catch (const std::exception& e) {
        std::cerr << "Критична помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
