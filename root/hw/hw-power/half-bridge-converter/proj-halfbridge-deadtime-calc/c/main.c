#include "stm32f4xx_hal.h"
#include <stdint.h>
#include <stdbool.h>

/* Розрахунок регістра мертвого часу DTG для ядра з тактовою частотою 168 МГц (TIM1 CLK = 168 МГц)
 * Крок таймера T_dtg = 1 / 168e6 = 5.95 нс.
 * Бажаний dead-time = 160 нс -> 160 / 5.95 = 27 тактів (DTG = 27). */
#define HALFBRIDGE_TIM1_DEADTIME_TICKS  27
#define HALFBRIDGE_PWM_PERIOD_TICKS    1680   /* 168 МГц / 1680 = 100 кГц */

extern TIM_HandleTypeDef htim1;

/**
 * @brief Конфігурація апаратного захисту Break Input (BKIN) та мертвого часу.
 */
void HalfBridge_HardwareInit(void)
{
    TIM_BreakDeadTimeConfigTypeDef sBreakDeadTimeConfig = {0};

    sBreakDeadTimeConfig.OffStateRunMode  = TIM_OSSR_ENABLE;
    sBreakDeadTimeConfig.OffStateIDLEMode = TIM_OSSI_ENABLE;
    sBreakDeadTimeConfig.LockLevel        = TIM_LOCKLEVEL_OFF;
    sBreakDeadTimeConfig.DeadTime         = HALFBRIDGE_TIM1_DEADTIME_TICKS;
    sBreakDeadTimeConfig.BreakState       = TIM_BREAK_ENABLE;
    sBreakDeadTimeConfig.BreakPolarity    = TIM_BREAKPOLARITY_HIGH;
    sBreakDeadTimeConfig.AutomaticOutput  = TIM_AUTOMATICOUTPUT_DISABLE;

    HAL_TIMEx_ConfigBreakDeadTime(&htim1, &sBreakDeadTimeConfig);
}

/**
 * @brief Попередній заряд бутстрепного конденсатора та плавний пуск (Soft-Start).
 */
void HalfBridge_StartWithSoftStart(uint32_t target_duty_percent)
{
    /* 1. Початковий нульовий коефіцієнт заповнення */
    __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, 0);

    /* 2. Відкриваємо ЛИШЕ нижній ключ (канал 1N) для попереднього заряду Cbs */
    HAL_TIMEx_PWMN_Start(&htim1, TIM_CHANNEL_1);
    
    /* Затримка 200 мкс для повного наповнення конденсатора крізь Rbs + Dbs */
    for (volatile uint32_t i = 0; i < 6000; i++) {
        __NOP();
    }

    /* 3. Вмикаємо комплементарний вихід верхнього ключа */
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);

    /* 4. Плавне наростання шпаруватості (Soft-Start) для уникнення кидків струму */
    uint32_t max_duty_ticks = (HALFBRIDGE_PWM_PERIOD_TICKS * target_duty_percent) / 100;
    for (uint32_t d = 0; d <= max_duty_ticks; d += 10) {
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, d);
        for (volatile uint32_t w = 0; w < 500; w++) {
            __NOP();
        }
    }
}

/**
 * @brief Аварійна безпечна зупинка напівмоста з миттєвим закриттям обох ключів.
 */
void HalfBridge_EmergencyStop(void)
{
    /* Миттєво скидаємо компаратор і гасимо обидва виходи */
    __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, 0);
    HAL_TIM_PWM_Stop(&htim1, TIM_CHANNEL_1);
    HAL_TIMEx_PWMN_Stop(&htim1, TIM_CHANNEL_1);
}
