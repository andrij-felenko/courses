// task_profiler.cpp - Реалізація методів TaskProfiler для C++20
#include "task_profiler.hpp"
#include <cstdio>
#include <array>

namespace RealTime {

namespace Hardware {
    inline volatile uint32_t& DEMCR   = *reinterpret_cast<volatile uint32_t*>(0xE000EDFCU);
    inline volatile uint32_t& DWT_CTRL = *reinterpret_cast<volatile uint32_t*>(0xE0001000U);
    inline volatile uint32_t& DWT_CYCCNT = *reinterpret_cast<volatile uint32_t*>(0xE0001004U);

    constexpr uint32_t DEMCR_TRCENA = (1U << 24);
    constexpr uint32_t DWT_CYCCNTENA = (1U << 0);
}

template <size_t MaxTasks>
void TaskProfiler<MaxTasks>::init_hardware() noexcept {
    // 1. Активація блоку трасування
    Hardware::DEMCR |= Hardware::DEMCR_TRCENA;
    
    // 2. Активація лічильника
    Hardware::DWT_CYCCNT = 0U;
    Hardware::DWT_CTRL |= Hardware::DWT_CYCCNTENA;

    // 3. Калібрування власного оверхеду
    const uint32_t start = read_cyccnt();
    const uint32_t stop = read_cyccnt();
    overhead_cyc_ = stop - start;
}

template <size_t MaxTasks>
inline uint32_t TaskProfiler<MaxTasks>::read_cyccnt() noexcept {
    return Hardware::DWT_CYCCNT;
}

// Явна інстанціація шаблону для розміру 8
template class TaskProfiler<8>;

} // namespace RealTime
