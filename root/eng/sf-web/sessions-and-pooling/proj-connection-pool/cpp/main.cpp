#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <cstring>
#include <unistd.h>
#include <poll.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>

class ConnectionPool {
public:
    struct Config {
        std::string host;
        int port{80};
        size_t maxSize{10};
        std::chrono::seconds idleTimeout{30};
    };

    class ConnectionHandle {
    public:
        ConnectionHandle(ConnectionPool& pool, int fd)
            : pool_(pool), fd_(fd), broken_(false) {}

        ~ConnectionHandle() {
            if (fd_ >= 0) {
                pool_.release(fd_, broken_);
            }
        }

        ConnectionHandle(const ConnectionHandle&) = delete;
        ConnectionHandle& operator=(const ConnectionHandle&) = delete;

        ConnectionHandle(ConnectionHandle&& other) noexcept
            : pool_(other.pool_), fd_(other.fd_), broken_(other.broken_) {
            other.fd_ = -1;
        }

        int fd() const noexcept { return fd_; }
        void markBroken() noexcept { broken_ = true; }

    private:
        ConnectionPool& pool_;
        int fd_{-1};
        bool broken_{false};
    };

    explicit ConnectionPool(Config config)
        : config_(std::move(config)) {}

    ~ConnectionPool() {
        std::lock_guard<std::mutex> lock(mutex_);
        for (const auto& entry : idleStack_) {
            ::close(entry.fd);
        }
        idleStack_.clear();
    }

    std::optional<ConnectionHandle> acquire(std::chrono::milliseconds waitTimeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        const auto deadline = std::chrono::steady_clock::now() + waitTimeout;

        while (true) {
            const auto now = std::chrono::steady_clock::now();

            // 1. Спроба взяти сокет зі стека LIFO
            while (!idleStack_.empty()) {
                auto entry = idleStack_.back();
                idleStack_.pop_back();

                // Перевірка таймауту бездіяльності
                if (now - entry.lastUsed > config_.idleTimeout) {
                    ::close(entry.fd);
                    continue;
                }

                // Перевірка працездатності каналу
                if (!isHealthy(entry.fd)) {
                    ::close(entry.fd);
                    continue;
                }

                activeLeased_++;
                return ConnectionHandle(*this, entry.fd);
            }

            // 2. Створення нового сокета, якщо є вільний ліміт
            if (activeLeased_ < config_.maxSize) {
                activeLeased_++;
                lock.unlock(); // Відпускаємо м'ютекс на час виконання connect()

                int newFd = createSocket(config_.host, config_.port);
                if (newFd < 0) {
                    lock.lock();
                    activeLeased_--;
                    cv_.notify_one();
                    return std::nullopt;
                }
                return ConnectionHandle(*this, newFd);
            }

            // 3. Очікування вивільнення з'єднання на condition_variable
            if (cv_.wait_until(lock, deadline) == std::cv_status::timeout) {
                return std::nullopt;
            }
        }
    }

private:
    struct SocketEntry {
        int fd;
        std::chrono::steady_clock::time_point lastUsed;
    };

    void release(int fd, bool broken) {
        std::lock_guard<std::mutex> lock(mutex_);
        activeLeased_--;

        if (broken) {
            ::close(fd);
        } else {
            if (idleStack_.size() < config_.maxSize) {
                idleStack_.push_back({fd, std::chrono::steady_clock::now()});
            } else {
                ::close(fd);
            }
        }
        cv_.notify_one();
    }

    static bool isHealthy(int fd) noexcept {
        pollfd pfd{};
        pfd.fd = fd;
        pfd.events = POLLIN | POLLHUP | POLLERR;

        int ret = ::poll(&pfd, 1, 0);
        if (ret < 0) return false;
        if (ret > 0) {
            char buf[1];
            ssize_t n = ::recv(fd, buf, 1, MSG_PEEK | MSG_DONTWAIT);
            if (n <= 0) return false;
        }
        return true;
    }

    static int createSocket(const std::string& host, int port) {
        addrinfo hints{}, *res = nullptr;
        hints.ai_family = AF_UNSPEC;
        hints.ai_socktype = SOCK_STREAM;

        std::string portStr = std::to_string(port);
        if (::getaddrinfo(host.c_str(), portStr.c_str(), &hints, &res) != 0) {
            return -1;
        }

        int sockfd = -1;
        for (auto p = res; p != nullptr; p = p->ai_next) {
            sockfd = ::socket(p->ai_family, p->ai_socktype, p->ai_protocol);
            if (sockfd < 0) continue;

            if (::connect(sockfd, p->ai_addr, p->ai_addrlen) == 0) {
                break;
            }
            ::close(sockfd);
            sockfd = -1;
        }
        ::freeaddrinfo(res);
        return sockfd;
    }

    Config config_;
    std::mutex mutex_;
    std::condition_variable cv_;
    std::vector<SocketEntry> idleStack_;
    size_t activeLeased_{0};
};
