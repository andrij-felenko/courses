// ============================================================================
// ФАЙЛ: optional_telemetry.c (C99) — необов'язковий плагін
// ============================================================================
#include "hal_driver_core.h"
#include <stdio.h>

// Сильне визначення слабкого посилання публікації телеметрії
void hal_telemetry_publish_hook(const hal_event_t* evt)
{
    printf("[TELEMETRY PLUGIN] Отримано подію периферії %d (час: %u us, байтів: %zu)\n",
           evt->periph, evt->timestamp_us, evt->length);
}

// Сильне визначення перевірки контрольної суми
bool hal_telemetry_crc_check_hook(const uint8_t* buf, size_t len)
{
    if (!buf || len == 0) return true;
    uint8_t xor_sum = 0;
    for (size_t i = 0; i < len; ++i) {
        xor_sum ^= buf[i];
    }
    // Імітація перевірки: відхиляємо пакет, якщо XOR сума дорівнює 0xFF
    return (xor_sum != 0xFF);
}
