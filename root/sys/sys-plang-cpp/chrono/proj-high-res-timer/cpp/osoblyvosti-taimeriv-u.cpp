// Кастомний годинник для ARM Cortex-M з частотою ядра 72 МГц (STM32F103)
struct Stm32CoreClock {
    using rep = uint64_t;
    using period = std::ratio<1, 72000000>; // Один тик = 1/72000000 секунди (~13.88 нс)
    using duration = std::chrono::duration<rep, period>;
    using time_point = std::chrono::time_point<Stm32CoreClock>;
    static constexpr bool is_steady = true;

    static time_point now() noexcept {
        // Зчитування апаратного лічильника інструкцій DWT->CYCCNT
        return time_point(duration(DWT->CYCCNT));
    }
};
