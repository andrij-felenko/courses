// C драйвер для мікроконтролерів STM32 на базі STM32 HAL
#include "stm32f4xx_hal.h"
#include <stdbool.h>

typedef struct {
    TIM_HandleTypeDef *htim;       // Таймер апаратного ШІМ
    uint32_t channel;             // Канал таймера
    GPIO_TypeDef *port;           // Порт виводу керування
    uint16_t pin;                 // Вивід GPIO
    uint32_t max_on_time_ms;      // Граничний час світіння до аварії
    uint32_t turn_on_tick;        // Мітка часу ввімкнення
    uint32_t watchdog_tick;       // Мітка останнього оновлення watchdog
    uint8_t duty_percent;         // Шпаруватість (0-100%)
    bool is_active;               // Прапорець активного стану
    bool safety_tripped;          // Прапорець аварійного блокування
} LaserDriver_t;

void LaserDriver_Init(LaserDriver_t *driver, TIM_HandleTypeDef *htim, uint32_t channel,
                      GPIO_TypeDef *port, uint16_t pin, uint32_t max_on_time_ms) {
    driver->htim = htim;
    driver->channel = channel;
    driver->port = port;
    driver->pin = pin;
    driver->max_on_time_ms = max_on_time_ms;
    driver->duty_percent = 100;
    driver->is_active = false;
    driver->safety_tripped = false;
    driver->watchdog_tick = HAL_GetTick();

    // Гарантоване початкове знеструмлення випромінювача
    HAL_GPIO_WritePin(driver->port, driver->pin, GPIO_PIN_RESET);
}

void LaserDriver_SetDuty(LaserDriver_t *driver, uint8_t duty_percent) {
    if (duty_percent > 100) duty_percent = 100;
    driver->duty_percent = duty_percent;

    if (driver->htim != NULL) {
        uint32_t autoreload = __HAL_TIM_GET_AUTORELOAD(driver->htim);
        uint32_t compare = (autoreload * duty_percent) / 100;
        __HAL_TIM_SET_COMPARE(driver->htim, driver->channel, compare);
    }
}

void LaserDriver_TriggerStrobe(LaserDriver_t *driver, uint32_t duration_us) {
    if (driver->safety_tripped) {
        return;
    }

    HAL_GPIO_WritePin(driver->port, driver->pin, GPIO_PIN_SET);
    driver->is_active = true;
    driver->turn_on_tick = HAL_GetTick();
    driver->watchdog_tick = driver->turn_on_tick;

    // Апаратна мікросекундна пауза на час кадрової експозиції
    uint32_t ticks = duration_us * (SystemCoreClock / 1000000U) / 5U;
    while (ticks--) {
        __NOP();
    }

    HAL_GPIO_WritePin(driver->port, driver->pin, GPIO_PIN_RESET);
    driver->is_active = false;
}

void LaserDriver_FeedWatchdog(LaserDriver_t *driver) {
    driver->watchdog_tick = HAL_GetTick();
}

void LaserDriver_Service(LaserDriver_t *driver) {
    uint32_t now = HAL_GetTick();

    // Аварійне знеструмлення при перевищенні тривалості світіння
    if (driver->is_active && (now - driver->turn_on_tick > driver->max_on_time_ms)) {
        HAL_GPIO_WritePin(driver->port, driver->pin, GPIO_PIN_RESET);
        if (driver->htim != NULL) {
            HAL_TIM_PWM_Stop(driver->htim, driver->channel);
        }
        driver->is_active = false;
        driver->safety_tripped = true;
    }

    // Аварійне блокування при зависанні суперциклу програми
    if (now - driver->watchdog_tick > 100) {
        HAL_GPIO_WritePin(driver->port, driver->pin, GPIO_PIN_RESET);
        if (driver->htim != NULL) {
            HAL_TIM_PWM_Stop(driver->htim, driver->channel);
        }
        driver->is_active = false;
        driver->safety_tripped = true;
    }
}

void LaserDriver_ResetFault(LaserDriver_t *driver) {
    HAL_GPIO_WritePin(driver->port, driver->pin, GPIO_PIN_RESET);
    driver->is_active = false;
    driver->safety_tripped = false;
    driver->watchdog_tick = HAL_GetTick();
}
