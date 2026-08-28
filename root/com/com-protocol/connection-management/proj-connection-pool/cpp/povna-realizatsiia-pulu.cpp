#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <chrono>
#include <mutex>
#include <condition_variable>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

class ConnectionPool;

class SocketConnection {
public:
    explicit SocketConnection(int fd) 
        : fd_(fd), createdAt_(Clock::now()), lastUsedAt_(createdAt_) {}

    ~SocketConnection() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SocketConnection(const SocketConnection&) = delete;
    SocketConnection& operator=(const SocketConnection&) = delete;

    int nativeHandle() const noexcept { return fd_; }

    bool isAlive() const noexcept {
        if (fd_ < 0) return false;
        char probe;
        ssize_t r = ::recv(fd_, &probe, 1, MSG_PEEK | MSG_DONTWAIT);
        if (r == 0) return false; // Сервер надіслав FIN
        if (r < 0) {
            return (errno == EAGAIN || errno == EWOULDBLOCK);
        }
        return false; // Залишковий трафік
    }

    void touch() noexcept { lastUsedAt_ = Clock::now(); }

    using Clock = std::chrono::steady_clock;
    Clock::time_point createdAt() const noexcept { return createdAt_; }
    Clock::time_point lastUsedAt() const noexcept { return lastUsedAt_; }

private:
    int fd_{-1};
    Clock::time_point createdAt_;
    Clock::time_point lastUsedAt_;
};

class ConnectionLease {
public:
    ConnectionLease(std::shared_ptr<ConnectionPool> pool, std::unique_ptr<SocketConnection> conn)
        : pool_(std::move(pool)), conn_(std::move(conn)) {}

    ~ConnectionLease();

    ConnectionLease(ConnectionLease&&) noexcept = default;
    ConnectionLease& operator=(ConnectionLease&&) noexcept = default;

    SocketConnection* operator->() noexcept { return conn_.get(); }
    SocketConnection& operator*() noexcept { return *conn_; }
    int fd() const noexcept { return conn_ ? conn_->nativeHandle() : -1; }

    void markBroken() noexcept { isBroken_ = true; }

private:
    std::shared_ptr<ConnectionPool> pool_;
    std::unique_ptr<SocketConnection> conn_;
    bool isBroken_{false};
};

class ConnectionPool : public std::enable_shared_from_this<ConnectionPool> {
public:
    struct Config {
        std::string host;
        int port{80};
        size_t maxCapacity{16};
        std::chrono::seconds maxIdleTime{30};
        std::chrono::seconds maxLifetime{300};
    };

    explicit ConnectionPool(Config config) : config_(std::move(config)) {}

    ~ConnectionPool() {
        shutdown();
    }

    std::unique_ptr<ConnectionLease> acquire(std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        auto deadline = std::chrono::steady_clock::now() + timeout;

        while (!isShutdown_) {
            auto now = std::chrono::steady_clock::now();

            // 1. Отримання валідного з'єднання з вершини LIFO-стека
            while (!idleStack_.empty()) {
                auto conn = std::move(idleStack_.back());
                idleStack_.pop_back();

                bool expired = ((now - conn->lastUsedAt()) > config_.maxIdleTime) ||
                               ((now - conn->createdAt()) > config_.maxLifetime);

                if (!expired && conn->isAlive()) {
                    ++activeCount_;
                    return std::make_unique<ConnectionLease>(shared_from_this(), std::move(conn));
                }
                // Застарілий або мертвий сокет знищується деструктором unique_ptr
            }

            // 2. Створення нового з'єднання, якщо ліміт активних не вичерпано
            if (activeCount_ < config_.maxCapacity) {
                ++activeCount_;
                lock.unlock(); // Звільняємо м'ютекс на час повільного мережевого виклику

                auto rawConn = openRawSocket();
                if (!rawConn) {
                    lock.lock();
                    --activeCount_;
                    cv_.notify_one();
                    return nullptr;
                }

                return std::make_unique<ConnectionLease>(shared_from_this(), std::move(rawConn));
            }

            // 3. Очікування на умовній змінній
            if (cv_.wait_until(lock, deadline) == std::cv_status::timeout) {
                return nullptr;
            }
        }
        return nullptr;
    }

    void release(std::unique_ptr<SocketConnection> conn, bool isBroken) {
        if (!conn) return;

        std::lock_guard<std::mutex> lock(mutex_);
        --activeCount_;

        auto now = std::chrono::steady_clock::now();
        bool expired = (now - conn->createdAt()) > config_.maxLifetime;

        if (!isBroken && !expired && !isShutdown_ && conn->isAlive()) {
            conn->touch();
            idleStack_.push_back(std::move(conn));
        }

        cv_.notify_one();
    }

    void shutdown() {
        std::lock_guard<std::mutex> lock(mutex_);
        isShutdown_ = true;
        idleStack_.clear();
        cv_.notify_all();
    }

private:
    std::unique_ptr<SocketConnection> openRawSocket() {
        int fd = ::socket(AF_INET, SOCK_STREAM, 0);
        if (fd < 0) return nullptr;

        struct sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(static_cast<uint16_t>(config_.port));
        if (::inet_pton(AF_INET, config_.host.c_str(), &addr.sin_addr) <= 0) {
            ::close(fd);
            return nullptr;
        }

        if (::connect(fd, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
            ::close(fd);
            return nullptr;
        }

        return std::make_unique<SocketConnection>(fd);
    }

    Config config_;
    std::vector<std::unique_ptr<SocketConnection>> idleStack_;
    size_t activeCount_{0};
    bool isShutdown_{false};
    std::mutex mutex_;
    std::condition_variable cv_;
};

inline ConnectionLease::~ConnectionLease() {
    if (pool_ && conn_) {
        pool_->release(std::move(conn_), isBroken_);
    }
}
