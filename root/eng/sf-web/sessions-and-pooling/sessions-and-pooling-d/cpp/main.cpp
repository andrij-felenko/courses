#include <vector>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <unistd.h>
#include <poll.h>
#include <sys/socket.h>

class ThreadSafeSocketPool {
public:
    explicit ThreadSafeSocketPool(size_t capacity)
        : capacity_(capacity) {}

    ~ThreadSafeSocketPool() {
        std::lock_guard<std::mutex> lock(mutex_);
        for (int fd : poolStack_) {
            ::close(fd);
        }
    }

    // RAII-дескриптор оренди сокета
    class ScopedConnection {
    public:
        ScopedConnection(ThreadSafeSocketPool& pool, int fd)
            : pool_(pool), fd_(fd) {}

        ~ScopedConnection() {
            if (fd_ >= 0) {
                pool_.release(fd_);
            }
        }

        ScopedConnection(const ScopedConnection&) = delete;
        ScopedConnection& operator=(const ScopedConnection&) = delete;

        ScopedConnection(ScopedConnection&& other) noexcept
            : pool_(other.pool_), fd_(other.fd_) {
            other.fd_ = -1;
        }

        int get() const noexcept { return fd_; }

    private:
        ThreadSafeSocketPool& pool_;
        int fd_{-1};
    };

    std::optional<ScopedConnection> acquire() {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_.wait(lock, [this] { return !poolStack_.empty(); });

        int fd = poolStack_.back();
        poolStack_.pop_back();
        lock.unlock();

        if (!isAlive(fd)) {
            ::close(fd);
            return std::nullopt;
        }

        return ScopedConnection(*this, fd);
    }

    void release(int fd) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (poolStack_.size() < capacity_) {
            poolStack_.push_back(fd);
            cv_.notify_one();
        } else {
            ::close(fd);
        }
    }

private:
    static bool isAlive(int fd) noexcept {
        pollfd pfd{fd, POLLIN | POLLHUP | POLLERR, 0};
        int res = ::poll(&pfd, 1, 0);
        if (res < 0) return false;
        if (res > 0) {
            char buf[1];
            if (::recv(fd, buf, 1, MSG_PEEK | MSG_DONTWAIT) <= 0) {
                return false;
            }
        }
        return true;
    }

    size_t capacity_;
    std::mutex mutex_;
    std::condition_variable cv_;
    std::vector<int> poolStack_;
};
