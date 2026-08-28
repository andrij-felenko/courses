#include <mutex>
#include <thread>
#include <chrono>

std::mutex mutex_a;
std::mutex mutex_b;

void safe_worker_1() {
    // std::lock атомарно захоплює довільну кількість м'ютексів
    // за алгоритмом запобігання дедлокам без прив'язки до порядку
    std::unique_lock<std::mutex> lock_a(mutex_a, std::defer_lock);
    std::unique_lock<std::mutex> lock_b(mutex_b, std::defer_lock);
    std::lock(lock_a, lock_b);

    std::this_thread::sleep_for(std::chrono::seconds(1));
}

void safe_worker_2() {
    // В C++17 доступний std::scoped_lock із RAII
    std::scoped_lock lock(mutex_b, mutex_a);

    std::this_thread::sleep_for(std::chrono::seconds(1));
}
