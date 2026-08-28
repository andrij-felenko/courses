#include <array>
#include "FreeRTOS.h"
#include "task.h"

// Статичний буфер через типізований std::array у C++
constexpr size_t ControlTaskStackSize = 256;
static std::array<StackType_t, ControlTaskStackSize> control_task_stack{};
static StaticTask_t control_task_tcb{};

TaskHandle_t handle = xTaskCreateStatic(
    &task_entry_function,
    "MotorCtrl",
    ControlTaskStackSize,
    nullptr,
    configMAX_PRIORITIES - 1,
    control_task_stack.data(),
    &control_task_tcb
);
