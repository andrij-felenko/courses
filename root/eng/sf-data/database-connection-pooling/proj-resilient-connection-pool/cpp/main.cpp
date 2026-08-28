#include <iostream>
#include <vector>
#include <memory>
#include <chrono>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <atomic>
#include <optional>
#include <span>
#include <stdexcept>
#include <unistd.h>

class DbConnection {
public:
    explicit DbConnection(int fd)
        : socket_fd_(fd),
          created_at_(std::chrono::steady_clock::now()),
          last_used_at_(created_at_),
          is_valid_(true) {}

    ~DbConnection() {
        if (socket_fd_ > 0) {
            ::close(socket_fd_);
        }
    }

    DbConnection(const DbConnection&) = delete;
    DbConnection& operator=(const DbConnection&) = delete;
    DbConnection(DbConnection&& other) noexcept
        : socket_fd_(std::exchange(other.socket_fd_, -1)),
          created_at_(other.created_at_),
          last_used_at_(other.last_used_at_),
          is_valid_(other.is_valid_) {}

    [[nodiscard]] int fd() const noexcept { return socket_fd_; }
    [[nodiscard]] bool isValid() const noexcept { return is_valid_ && socket_fd_ > 0; }
    [[nodiscard]] std::chrono::steady_clock::time_point createdAt() const noexcept { return created_at_; }
    [[nodiscard]] std::chrono::steady_clock::time_point lastUsedAt() const noexcept { return last_used_at_; }

    void touch() noexcept { last_used_at_ = std::chrono::steady_clock::now(); }
    void markInvalid() noexcept { is_valid_ = false; }

private:
    int socket_fd_{-1};
    std::chrono::steady_clock::time_point created_at_;
    std::chrono::steady_clock::time_point last_used_at_;
    bool is_valid_{true};
};

struct PoolConfig {
    size_t capacity{16};
    std::chrono::milliseconds acquire_timeout{1000};
    std::chrono::milliseconds idle_validation_timeout{10000};
    std::chrono::milliseconds max_lifetime{1800000}; // 30 хв
    std::chrono::milliseconds leak_threshold{5000};     // 5 с
};

class ConnectionPool;

/* RAII-обгортка орендованого з'єднання */
class ConnectionLease {
public:
    ConnectionLease(std::shared_ptr<ConnectionPool> pool, std::unique_ptr<DbConnection> conn)
        : pool_(std::move(pool)), conn_(std::move(conn)) {}

    ~ConnectionLease();

    ConnectionLease(const ConnectionLease&) = delete;
    ConnectionLease& operator=(const ConnectionLease&) = delete;
    ConnectionLease(ConnectionLease&&) noexcept = default;
    ConnectionLease& operator=(ConnectionLease&&) noexcept = default;

    [[nodiscard]] DbConnection* get() const noexcept { return conn_.get(); }
    [[nodiscard]] DbConnection* operator->() const noexcept { return conn_.get(); }
    [[nodiscard]] DbConnection& operator*() const noexcept { return *conn_; }
    [[nodiscard]] explicit operator bool() const noexcept { return conn_ != nullptr; }

private:
    std::shared_ptr<ConnectionPool> pool_;
    std::unique_ptr<DbConnection> conn_;
};

class ConnectionPool : public std::enable_shared_from_this<ConnectionPool> {
public:
    static std::shared_ptr<ConnectionPool> create(PoolConfig config) {
        auto pool = std::shared_ptr<ConnectionPool>(new ConnectionPool(config));
        pool->initialize();
        return pool;
    }

    ~ConnectionPool() {
        shutdown();
    }

    [[nodiscard]] std::optional<ConnectionLease> acquire() {
        std::unique_lock<std::mutex> lock(mutex_);

        auto deadline = std::chrono::steady_clock::now() + config_.acquire_timeout;

        while (idle_connections_.empty() && !is_shutdown_) {
            if (cv_.wait_until(lock, deadline) == std::cv_status::timeout) {
                return std::nullopt; // вичерпано таймаут очікування
            }
        }

        if (is_shutdown_) {
            return std::nullopt;
        }

        auto conn = std::move(idle_connections_.back());
        idle_connections_.pop_back();

        auto now = std::chrono::steady_clock::now();

        // Перевірка терміну життя (Max Lifetime)
        if (now - conn->createdAt() > config_.max_lifetime) {
            conn = createRawConnection();
        }
        // Перевірка після простою
        else if (now - conn->lastUsedAt() > config_.idle_validation_timeout) {
            if (!conn->isValid()) {
                conn = createRawConnection();
            }
        }

        active_leases_++;
        return ConnectionLease(shared_from_this(), std::move(conn));
    }

    void release(std::unique_ptr<DbConnection> conn) {
        if (!conn) return;

        conn->touch();
        std::unique_lock<std::mutex> lock(mutex_);

        idle_connections_.push_back(std::move(conn));
        active_leases_--;

        cv_.notify_one();

        if (is_shutdown_ && active_leases_ == 0) {
            drain_cv_.notify_all();
        }
    }

    void shutdown() {
        {
            std::unique_lock<std::mutex> lock(mutex_);
            if (is_shutdown_) return;
            is_shutdown_ = true;
            cv_.notify_all();
        }

        // Очікування завершення активних транзакцій (дренаж)
        {
            std::unique_lock<std::mutex> lock(mutex_);
            drain_cv_.wait(lock, [this]() { return active_leases_ == 0; });
        }

        if (watchdog_thread_.joinable()) {
            watchdog_thread_.join();
        }

        std::unique_lock<std::mutex> lock(mutex_);
        idle_connections_.clear();
    }

private:
    explicit ConnectionPool(PoolConfig config)
        : config_(config), is_shutdown_(false), active_leases_(0) {}

    void initialize() {
        for (size_t i = 0; i < config_.capacity; ++i) {
            idle_connections_.push_back(createRawConnection());
        }
        watchdog_thread_ = std::thread(&ConnectionPool::watchdogLoop, this);
    }

    std::unique_ptr<DbConnection> createRawConnection() {
        static std::atomic<int> fd_gen{200};
        return std::make_unique<DbConnection>(fd_gen.fetch_add(1));
    }

    void watchdogLoop() {
        while (true) {
            std::this_thread::sleep_for(std::chrono::milliseconds(500));

            std::unique_lock<std::mutex> lock(mutex_);
            if (is_shutdown_ && active_leases_ == 0) {
                break;
            }
        }
    }

    PoolConfig config_;
    std::mutex mutex_;
    std::condition_variable cv_;
    std::condition_variable drain_cv_;
    std::vector<std::unique_ptr<DbConnection>> idle_connections_;
    std::atomic<size_t> active_leases_{0};
    bool is_shutdown_{false};
    std::thread watchdog_thread_;
};

inline ConnectionLease::~ConnectionLease() {
    if (pool_ && conn_) {
        pool_->release(std::move(conn_));
    }
}
