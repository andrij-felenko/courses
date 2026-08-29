#pragma once

#include <chrono>

#include "esp_log.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/timers.h"

#include "portal/esp_result.hpp"

namespace portal {

/*
 * Планує перезапуск програмним таймером FreeRTOS.
 *
 * Викликати esp_restart() просто в обробнику HTTP не можна: відповідь
 * ще лежить у буфері сокета, і замість «збережено» клієнт побачить
 * обірване з'єднання. Затримка дає стеку TCP/IP віддати тіло відповіді
 * й закрити сесію обміном FIN/ACK.
 */
[[nodiscard]] inline Status scheduleReboot(std::chrono::milliseconds delay) noexcept
{
    const auto ticks = pdMS_TO_TICKS(delay.count());
    if (ticks == 0) {
        return std::unexpected(ESP_ERR_INVALID_ARG);
    }

    /* Таймер створюється раз і живе далі: повторний виклик лише перезаводить його. */
    static TimerHandle_t timer = xTimerCreate(
        "reboot", ticks, pdFALSE, nullptr,
        [](TimerHandle_t) {
            ESP_LOGI("reboot", "Плановий перезапуск системи");
            esp_restart();
        });

    if (timer == nullptr) {
        return std::unexpected(ESP_ERR_NO_MEM);
    }

    if (xTimerChangePeriod(timer, ticks, 0) != pdPASS) {
        return std::unexpected(ESP_FAIL);
    }

    /* Команда йде в чергу служби таймерів; блокуватися в обробнику не можна. */
    if (xTimerStart(timer, 0) != pdPASS) {
        return std::unexpected(ESP_FAIL);
    }

    return {};
}

}  // namespace portal
