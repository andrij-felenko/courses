template<class Clock, class Duration>
std::cv_status wait_until(
    std::unique_lock<std::mutex>& lock,
    const std::chrono::time_point<Clock, Duration>& abs_time
); // (1)

template<class Clock, class Duration, class Predicate>
bool wait_until(
    std::unique_lock<std::mutex>& lock,
    const std::chrono::time_point<Clock, Duration>& abs_time,
    Predicate pred
); // (2)
