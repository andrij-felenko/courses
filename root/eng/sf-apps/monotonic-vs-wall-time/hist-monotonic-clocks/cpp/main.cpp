#include <condition_variable>
#include <mutex>
#include <chrono>

std::condition_variable cv;
std::mutex m;
std::unique_lock<std::mutex> lock(m);

// У C++11 std::condition_variable::wait_until
// за замовчуванням підтримує дедлайн за std::chrono::steady_clock:
auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(30);
cv.wait_until(lock, deadline, [&]() { return condition_is_met(); });
