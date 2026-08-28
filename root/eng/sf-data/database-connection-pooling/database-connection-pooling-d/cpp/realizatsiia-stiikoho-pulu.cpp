#include <iostream>
#include <vector>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <optional>
#include <stdexcept>
#include <random>

class DbConnection {
public:
    explicit DbConnection(int id)
        : socket_fd_(id), created_at_(Clock::now()), last_used_at_(created_at_) {}

    ~DbConnection() {
        // Закриття сокета у деструкторі (RAII)
    }

    bool ping() const noexcept {
        return socket_fd_ >= 0;
    }

    void reset_state() noexcept {
        // Відкат незафіксованих транзакцій (ROLLBACK)
    }

    void mark_used() noexcept {
        last_used_at_ = Clock::now();
    }

    [[nodiscard]] auto last_used_at() const noexcept { return last_used_at_; }
    [[nodiscard]] auto created_at() const noexcept { return created_at_; }
    [[nodiscard]] int id() const noexcept { return socket_fd_; }

private:
    using Clock = std::chrono::steady_clock;
    int socket_fd_;
    Clock::time_point created_at_;
    Clock::time_point last_used_at_;
};

class ConnectionPool;

// RAII обгортка для автоматичного повернення з'єднання у пул
class ScopedConnection {
public:
    ScopedConnection(std::unique_ptr<DbConnection> conn, ConnectionPool& pool)
        : conn_(std::move(conn)), pool_(pool) {}

    ~ScopedConnection();

    ScopedConnection(const ScopedConnection&) = delete;
    ScopedConnection& operator=(const ScopedConnection&) = delete;

    ScopedConnection(ScopedConnection&& other) noexcept
        : conn_(std::move(other.conn_)), pool_(other.pool_) {}

    DbConnection* operator->() noexcept { return conn_.get(); }
    DbConnection& operator*() noexcept { return *conn_; }
    [[nodiscard]] DbConnection* get() noexcept { return conn_.get(); }

private:
    std::unique_ptr<DbConnection> conn_;
    ConnectionPool& pool_;
};

class ConnectionPool {
public:
    using Milliseconds = std::chrono::milliseconds;

    ConnectionPool(size_t capacity, Milliseconds acquire_timeout, Milliseconds idle_timeout)
        : capacity_(capacity), acquire_timeout_(acquire_timeout), idle_timeout_(idle_timeout) {
        
        for (size_t i = 0; i < capacity_; ++i) {
            idle_connections_.push_back(std::make_unique<DbConnection>(static_cast<int>(i + 1)));
        }
    }

    ~ConnectionPool() {
        shutdown();
    }

    std::optional<ScopedConnection> acquire() {
        std::unique_lock<std::mutex> lock(mutex_);
        const auto deadline = std::chrono::steady_clock::now() + acquire_timeout_;

        while (idle_connections_.empty()) {
            if (is_closed_) {
                return std::nullopt;
            }
            if (cv_.wait_until(lock, deadline) == std::cv_status::timeout) {
                return std::nullopt; // Таймаут очікування оренди
            }
        }

        if (is_closed_) return std::nullopt;

        auto conn = std::move(idle_connections_.back());
        idle_connections_.pop_back();
        lock.unlock();

        // Валідація сокета за часом бездіяльності
        const auto now = std::chrono::steady_clock::now();
        if (now - conn->last_used_at() > idle_timeout_) {
            if (!conn->ping()) {
                conn = std::make_unique<DbConnection>(conn->id() + 1000);
            }
        }

        return ScopedConnection(std::move(conn), *this);
    }

    void release(std::unique_ptr<DbConnection> conn) noexcept {
        if (!conn) return;

        conn->reset_state();
        conn->mark_used();

        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (!is_closed_ && idle_connections_.size() < capacity_) {
                idle_connections_.push_back(std::move(conn));
                cv_.notify_one();
                return;
            }
        }
        // Якщо пул закрито, conn автоматично знищується тут
    }

    void shutdown() noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        is_closed_ = true;
        idle_connections_.clear();
        cv_.notify_all();
    }

private:
    const size_t capacity_;
    const Milliseconds acquire_timeout_;
    const Milliseconds idle_timeout_;

    std::mutex mutex_;
    std::condition_variable cv_;
    std::vector<std::unique_ptr<DbConnection>> idle_connections_;
    bool is_closed_{false};
};

ScopedConnection::~ScopedConnection() {
    if (conn_) {
        pool_.release(std::move(conn_));
    }
}
