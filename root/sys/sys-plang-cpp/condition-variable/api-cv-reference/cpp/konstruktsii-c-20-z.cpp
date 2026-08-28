template<class Lock, class Predicate>
bool wait(
    Lock& lock,
    std::stop_token stoken,
    Predicate pred
); // (1) C++20

template<class Lock, class Rep, class Period, class Predicate>
bool wait_for(
    Lock& lock,
    std::stop_token stoken,
    const std::chrono::duration<Rep, Period>& rel_time,
    Predicate pred
); // (2) C++20

template<class Lock, class Clock, class Duration, class Predicate>
bool wait_until(
    Lock& lock,
    std::stop_token stoken,
    const std::chrono::time_point<Clock, Duration>& abs_time,
    Predicate pred
); // (3) C++20
