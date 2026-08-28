#include <iostream>
#include <vector>
#include <deque>
#include <thread>
#include <atomic>
#include <mutex>
#include <functional>
#include <random>
#include <memory>
#include <optional>
#include <span>

class WorkStealingPool {
public:
    using Task = std::function<void()>;

    explicit WorkStealingPool(size_t num_threads = std::thread::hardware_concurrency())
        : running_(true), num_threads_(std::max<size_t>(1, num_threads)), deques_(num_threads_) {
        workers_.reserve(num_threads_);
        for (size_t i = 0; i < num_threads_; ++i) {
            workers_.emplace_back([this, i] { worker_loop(i); });
        }
    }

    ~WorkStealingPool() {
        running_.store(false, std::memory_order_release);
        for (auto &worker : workers_) {
            if (worker.joinable()) {
                worker.join();
            }
        }
    }

    void submit(Task task, size_t target_worker = 0) {
        size_t idx = target_worker % num_threads_;
        deques_[idx].push_bottom(std::move(task));
    }

    size_t worker_count() const noexcept {
        return num_threads_;
    }

private:
    struct alignas(64) ThreadDeque {
        std::deque<Task> tasks;
        mutable std::mutex lock;

        void push_bottom(Task task) {
            std::lock_guard<std::mutex> guard(lock);
            tasks.push_back(std::move(task));
        }

        std::optional<Task> pop_bottom() {
            std::lock_guard<std::mutex> guard(lock);
            if (tasks.empty()) {
                return std::nullopt;
            }
            Task t = std::move(tasks.back());
            tasks.pop_back();
            return t;
        }

        std::optional<Task> steal_top() {
            std::unique_lock<std::mutex> guard(lock, std::try_to_lock);
            if (!guard.owns_lock() || tasks.empty()) {
                return std::nullopt;
            }
            Task t = std::move(tasks.front());
            tasks.pop_front();
            return t;
        }
    };

    void worker_loop(size_t worker_id) {
        thread_local std::mt19937 rng(static_cast<uint32_t>(worker_id + 42));
        std::uniform_int_distribution<size_t> dist(0, num_threads_ - 1);

        while (running_.load(std::memory_order_acquire)) {
            if (auto task = deques_[worker_id].pop_bottom()) {
                (*task)();
                continue;
            }

            bool stolen = false;
            if (num_threads_ > 1) {
                size_t victim = dist(rng);
                if (victim != worker_id) {
                    if (auto task = deques_[victim].steal_top()) {
                        (*task)();
                        stolen = true;
                    }
                }
            }

            if (!stolen) {
                std::this_thread::yield();
            }
        }
    }

    std::atomic<bool> running_;
    size_t num_threads_;
    std::vector<ThreadDeque> deques_;
    std::vector<std::thread> workers_;
};
