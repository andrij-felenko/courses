// Фрагмент RTOS хуків у стилі C++20
#include "task_profiler.hpp"

extern "C" void vApplicationTaskHookIn(void* task_handle, uint32_t task_id) noexcept;
extern "C" void vApplicationTaskHookOut(void* task_handle, uint32_t task_id) noexcept;

namespace {
    RealTime::TaskProfiler<8> g_system_profiler(168'000'000U);
}

extern "C" void vApplicationTaskHookIn(void* /*task_handle*/, uint32_t task_id) noexcept {
    g_system_profiler.enter(static_cast<uint8_t>(task_id));
}

extern "C" void vApplicationTaskHookOut(void* /*task_handle*/, uint32_t task_id) noexcept {
    g_system_profiler.exit(static_cast<uint8_t>(task_id));
}
