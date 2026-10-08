#pragma once

#include <cstdint>
#include <cstdio>
#include <cstring>
#include <array>
#include <string_view>

#if __has_include("stm32f4xx_hal.h")
#include "stm32f4xx_hal.h"
#elif __has_include("stm32_hal.h")
#include "stm32_hal.h"
#else
// Резервні визначення типів HAL
#ifndef HAL_OK
typedef enum {
    HAL_OK = 0x00U,
    HAL_ERROR = 0x01U,
    HAL_BUSY = 0x02U,
    HAL_TIMEOUT = 0x03U
} HAL_StatusTypeDef;
#endif

typedef struct {
    uint32_t State;
} UART_HandleTypeDef;
#endif

namespace telemetry {

/**
 * @brief Завадостійкий клас телеметрії для передачі вимірювань через UART STM32
 * Використовує статичний буфер фіксованого розміру без виділення пам'яті у купі (DRAM).
 */
class UartTelemetry {
public:
    static constexpr size_t kBufferSize = 128;
    static constexpr uint32_t kDefaultTimeoutMs = 100;

    /**
     * @brief Конструктор модуля телеметрії
     * @param huart Вказівник на хендл UART STM32 HAL
     * @param timeout_ms Таймаут передавання даних
     */
    explicit UartTelemetry(UART_HandleTypeDef* huart, uint32_t timeout_ms = kDefaultTimeoutMs)
        : huart_(huart), timeout_ms_(timeout_ms) {}

    /**
     * @brief Передає довільний текстовий рядок без динамічної пам'яті
     */
    HAL_StatusTypeDef sendString(std::string_view message) {
        if (!huart_ || message.empty()) {
            return HAL_ERROR;
        }

        size_t len = message.length();
        if (len >= kBufferSize) {
            len = kBufferSize - 1;
        }

        std::memcpy(buffer_.data(), message.data(), len);
        buffer_[len] = '\0';

        return transmitBuffer(len);
    }

    /**
     * @brief Форматує та завадостійко передає параметри монітора живлення INA219
     * @param v_bus_V Напруга шини (В)
     * @param v_shunt_mV Напруга на шунті (мВ)
     * @param current_mA Струм навантаження (мА)
     * @param power_mW Потужність (мВт)
     * @param is_ovf Прапорець математичного переповнення
     */
    HAL_StatusTypeDef sendPowerData(float v_bus_V, float v_shunt_mV, float current_mA, float power_mW, bool is_ovf = false) {
        if (!huart_) {
            return HAL_ERROR;
        }

        // Завадостійкий формат із контрольною структурою кадру
        int len = std::snprintf(buffer_.data(), kBufferSize,
            "$PWR,V_BUS=%.3f,V_SHUNT=%.2f,I=%.2f,P=%.2f,OVF=%d*\r\n",
            static_cast<double>(v_bus_V),
            static_cast<double>(v_shunt_mV),
            static_cast<double>(current_mA),
            static_cast<double>(power_mW),
            is_ovf ? 1 : 0);

        if (len <= 0) {
            return HAL_ERROR;
        }

        size_t transmit_len = static_cast<size_t>(len);
        if (transmit_len >= kBufferSize) {
            transmit_len = kBufferSize - 1;
        }

        return transmitBuffer(transmit_len);
    }

private:
    HAL_StatusTypeDef transmitBuffer(size_t len) {
#if defined(HAL_UART_MODULE_ENABLED) || defined(STM32F4xx_HAL_H) || defined(HAL_OK)
        // Завадостійка передача з обробкою стану зайнятості периферії HAL_BUSY
        HAL_StatusTypeDef status = HAL_UART_Transmit(
            huart_,
            reinterpret_cast<const uint8_t*>(buffer_.data()),
            static_cast<uint16_t>(len),
            timeout_ms_
        );

        if (status == HAL_BUSY) {
            // Повторна спроба відправки при виникненні тимчасового блокування UART
            status = HAL_UART_Transmit(
                huart_,
                reinterpret_cast<const uint8_t*>(buffer_.data()),
                static_cast<uint16_t>(len),
                timeout_ms_
            );
        }
        return status;
#else
        (void)len;
        return HAL_OK;
#endif
    }

    UART_HandleTypeDef* huart_{nullptr};
    uint32_t timeout_ms_{kDefaultTimeoutMs};
    std::array<char, kBufferSize> buffer_{};
};

} // namespace telemetry
