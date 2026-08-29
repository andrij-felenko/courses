// profiler_trace.hpp — під'єднання C++-профілювальника до гачків FreeRTOS.
//
// FreeRTOSConfig.h читається з середини ядра й компілюється як C, тож назовні
// стирчать дві функції з C-зв'язуванням, а сам об'єкт живе тут:
//
//     #define configUSE_TRACE_FACILITY 1
//     void profiler_trace_switch_in(unsigned task_number);
//     void profiler_trace_switch_out(unsigned task_number);
//     #define traceTASK_SWITCHED_IN()  profiler_trace_switch_in((unsigned)pxCurrentTCB->uxTaskNumber)
//     #define traceTASK_SWITCHED_OUT() profiler_trace_switch_out((unsigned)pxCurrentTCB->uxTaskNumber)
//
// Номер задачі виставляють викликом vTaskSetTaskNumber(handle, id) одразу
// після xTaskCreate — тим самим id, під яким її зареєстровано тут. Задачі без
// номера (idle, задача таймерів) мають 0, тож нульовий слот лишаємо їм.
#pragma once

#include "task_profiler.hpp"

namespace rt {

inline constexpr std::size_t kSystemTasks = 8;
inline constexpr std::uint32_t kSystemClockHz = 168'000'000U;

// Один екземпляр на систему. Функція, а не глобальна змінна: конструювання
// відбувається при першому зверненні, а не в непередбачуваному порядку
// статичної ініціалізації до виклику SystemInit().
[[nodiscard]] inline TaskProfiler<kSystemTasks>& system_profiler() noexcept
{
    static TaskProfiler<kSystemTasks> instance{kSystemClockHz};
    return instance;
}

} // namespace rt

extern "C" {

// Гачок спрацьовує щоразу, коли планувальник обрав нову задачу. Вимірюваний
// інтервал — це ЗРІЗ виконання між двома перемиканнями, а не весь прохід
// задачі: витіснену задачу планувальник спершу «виводить», і зріз закривається
// достроково.
inline void profiler_trace_switch_in(unsigned task_number)
{
    if (task_number < rt::kSystemTasks) {
        rt::system_profiler().enter(static_cast<std::uint8_t>(task_number));
    }
}

inline void profiler_trace_switch_out(unsigned task_number)
{
    if (task_number < rt::kSystemTasks) {
        rt::system_profiler().exit(static_cast<std::uint8_t>(task_number));
    }
}

} // extern "C"
