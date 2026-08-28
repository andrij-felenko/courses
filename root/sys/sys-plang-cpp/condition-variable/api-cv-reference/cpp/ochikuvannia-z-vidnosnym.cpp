template<class Rep, class Period>
std::cv_status wait_for(
    std::unique_lock<std::mutex>& lock,
    const std::chrono::duration<Rep, Period>& rel_time
); // (1)

template<class Rep, class Period, class Predicate>
bool wait_for(
    std::unique_lock<std::mutex>& lock,
    const std::chrono::duration<Rep, Period>& rel_time,
    Predicate pred
); // (2)
