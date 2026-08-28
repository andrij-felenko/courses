namespace std {
    class condition_variable_any {
    public:
        // Базове переривне очікування
        template<class Lock, class Predicate>
        bool wait(Lock& lock, stop_token stoken, Predicate pred);

        // Переривне очікування з відносним таймаутом
        template<class Lock, class Rep, class Period, class Predicate>
        bool wait_for(Lock& lock, stop_token stoken,
                      const chrono::duration<Rep, Period>& rel_time,
                      Predicate pred);

        // Переривне очікування з абсолютним часом
        template<class Lock, class Clock, class Duration, class Predicate>
        bool wait_until(Lock& lock, stop_token stoken,
                        const chrono::time_point<Clock, Duration>& abs_time,
                        Predicate pred);
    };
}
