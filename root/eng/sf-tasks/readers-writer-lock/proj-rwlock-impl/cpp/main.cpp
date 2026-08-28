#include <chrono>
#include <condition_variable>
#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

class WritePreferringRwLock {
public:
    WritePreferringRwLock() = default;
    ~WritePreferringRwLock() = default;

    WritePreferringRwLock(const WritePreferringRwLock&) = delete;
    WritePreferringRwLock& operator=(const WritePreferringRwLock&) = delete;

    void lock_shared() {
        std::unique_lock<std::mutex> lock(mutex_);
        cond_readers_.wait(lock, [this]() {
            return !writer_active_ && writers_waiting_ == 0;
        });
        ++readers_;
    }

    void unlock_shared() {
        std::unique_lock<std::mutex> lock(mutex_);
        --readers_;
        if (readers_ == 0 && writers_waiting_ > 0) {
            cond_writers_.notify_one();
        }
    }

    void lock() {
        std::unique_lock<std::mutex> lock(mutex_);
        ++writers_waiting_;
        cond_writers_.wait(lock, [this]() {
            return !writer_active_ && readers_ == 0;
        });
        --writers_waiting_;
        writer_active_ = true;
    }

    void unlock() {
        std::unique_lock<std::mutex> lock(mutex_);
        writer_active_ = false;
        if (writers_waiting_ > 0) {
            cond_writers_.notify_one();
        } else {
            cond_readers_.notify_all();
        }
    }

private:
    std::mutex              mutex_;
    std::condition_variable cond_readers_;
    std::condition_variable cond_writers_;
    int                     readers_ = 0;
    int                     writers_waiting_ = 0;
    bool                    writer_active_ = false;
};

// RAII-обгортки для автоматичного звільнення блокувань при розгортанні стека
class SharedLockGuard {
public:
    explicit SharedLockGuard(WritePreferringRwLock& lock) : lock_(lock) {
        lock_.lock_shared();
    }
    ~SharedLockGuard() {
        lock_.unlock_shared();
    }
    SharedLockGuard(const SharedLockGuard&) = delete;
    SharedLockGuard& operator=(const SharedLockGuard&) = delete;

private:
    WritePreferringRwLock& lock_;
};

class ExclusiveLockGuard {
public:
    explicit ExclusiveLockGuard(WritePreferringRwLock& lock) : lock_(lock) {
        lock_.lock();
    }
    ~ExclusiveLockGuard() {
        lock_.unlock();
    }
    ExclusiveLockGuard(const ExclusiveLockGuard&) = delete;
    ExclusiveLockGuard& operator=(const ExclusiveLockGuard&) = delete;

private:
    WritePreferringRwLock& lock_;
};
