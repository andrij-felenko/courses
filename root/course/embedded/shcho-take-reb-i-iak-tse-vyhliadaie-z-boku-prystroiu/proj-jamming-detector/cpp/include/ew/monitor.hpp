#pragma once

#include <cstdint>

#include "FreeRTOS.h"
#include "task.h"

namespace ew {

// Заводить чергу вибірок і потік телеметрії. Викликати один раз до
// vTaskStartScheduler(), пріоритет — нижчий за радіодрайвер.
void startMonitor(UBaseType_t priority) noexcept;

// Скільки вибірок згоріло на переповненій черзі — суто діагностика.
[[nodiscard]] std::uint32_t droppedSamples() noexcept;

} // namespace ew

// Обробник переривання DIO1 трансивера: підключається до таблиці векторів,
// тому має мати C-зв'язування.
extern "C" void ew_monitor_dio1_isr();
