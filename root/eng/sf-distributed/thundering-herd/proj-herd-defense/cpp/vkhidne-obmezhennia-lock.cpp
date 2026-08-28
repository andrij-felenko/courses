// C++20 server worker using SO_REUSEPORT, EPOLLEXCLUSIVE and atomic Token Bucket
#include <iostream>
#include <atomic>
#include <chrono>
#include <thread>
#include <vector>
#include <cstring>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <netinet/in.h>
#include <unistd.h>
#include <fcntl.h>

class AtomicTokenBucket {
public:
    AtomicTokenBucket(double capacity, double refill_rate)
        : capacity_(capacity), refill_rate_(refill_rate),
          tokens_(capacity),
          last_update_(std::chrono::steady_clock::now().time_since_epoch().count()) {}

    bool try_consume() {
        const auto now = std::chrono::steady_clock::now().time_since_epoch().count();
        auto last = last_update_.load(std::memory_order_relaxed);

        while (true) {
            const double elapsed = static_cast<double>(now - last) / 1e9;
            double current = tokens_.load(std::memory_order_relaxed);
            double updated = std::min(capacity_, current + elapsed * refill_rate_);

            if (updated < 1.0) {
                return false; // Admission rejected: rate limit exceeded
            }

            if (tokens_.compare_exchange_weak(current, updated - 1.0,
                                             std::memory_order_release,
                                             std::memory_order_relaxed)) {
                last_update_.store(now, std::memory_order_relaxed);
                return true;
            }
        }
    }

private:
    const double capacity_;
    const double refill_rate_;
    std::atomic<double> tokens_;
    std::atomic<long long> last_update_;
};

class ReusePortServerWorker {
public:
    ReusePortServerWorker(int id, int port, AtomicTokenBucket& limiter)
        : worker_id_(id), port_(port), limiter_(limiter) {}

    void run(std::stop_token stop_tok) {
        int listen_fd = ::socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK, 0);
        if (listen_fd < 0) return;

        int opt = 1;
        ::setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
        ::setsockopt(listen_fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt));

        struct sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(port_);

        if (::bind(listen_fd, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0 ||
            ::listen(listen_fd, 4096) < 0) {
            ::close(listen_fd);
            return;
        }

        int epoll_fd = ::epoll_create1(0);
        struct epoll_event ev{};
        ev.events = EPOLLIN | EPOLLET | EPOLLEXCLUSIVE;
        ev.data.fd = listen_fd;
        ::epoll_ctl(epoll_fd, EPOLL_CTL_ADD, listen_fd, &ev);

        struct epoll_event events[64];
        while (!stop_tok.stop_requested()) {
            int nfds = ::epoll_wait(epoll_fd, events, 64, 200);
            for (int i = 0; i < nfds; ++i) {
                if (events[i].data.fd == listen_fd) {
                    while (true) {
                        struct sockaddr_in client_addr{};
                        socklen_t client_len = sizeof(client_addr);
                        int client_fd = ::accept4(listen_fd,
                                                  reinterpret_cast<struct sockaddr*>(&client_addr),
                                                  &client_len, SOCK_NONBLOCK);
                        if (client_fd < 0) {
                            if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                            break;
                        }

                        if (!limiter_.try_consume()) {
                            // Швидке скидання з'єднання при перевантаженні (Herd Protection)
                            ::close(client_fd);
                            continue;
                        }

                        // Обробка дозволеного з'єднання
                        ::close(client_fd);
                    }
                }
            }
        }

        ::close(epoll_fd);
        ::close(listen_fd);
    }

private:
    int worker_id_;
    int port_;
    AtomicTokenBucket& limiter_;
};
