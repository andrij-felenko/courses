#include <memory>
#include <thread>
#include <vector>

namespace physics::nonlinear::api {

class ThreadPool {
public:
    explicit ThreadPool(std::size_t thread_count = std::thread::hardware_concurrency());
    ~ThreadPool();

    ThreadPool(const ThreadPool&) = delete;
    ThreadPool& operator=(const ThreadPool&) = delete;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace physics::nonlinear::api
