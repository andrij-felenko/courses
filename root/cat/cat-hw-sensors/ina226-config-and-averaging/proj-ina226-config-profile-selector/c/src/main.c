/**
 * @file main.c
 * @brief Приклад динамічного керування профілями INA226 та неблокуючого зчитування телеметрії.
 *
 * Ініціалізує периферію, створює 3 профілі (Low-Power, Dynamic, High-Precision),
 * перемикає профілі залежно від навантаження та виводить виміряні величини.
 */

#include <stdio.h>
#include <stdbool.h>
#include "i2c_driver.h"
#include "ina226.h"

/* Константи системного моніторингу */
#define INA226_I2C_ADDR             0x40U    /**< I2C адреса (A0=GND, A1=GND) */
#define SHUNT_RESISTOR_OHM          0.02f    /**< Шунт 20 мОм */
#define MAX_CURRENT_AMP             8.0f     /**< Максимальний струм 8 А */

/* Визначення робочих профілів */
static const ina226_profile_t g_profile_low_power = {
    .avg = INA226_AVG_1,
    .vshct = INA226_CONV_TIME_140US,
    .vbusct = INA226_CONV_TIME_140US,
    .mode = INA226_MODE_BOTH_CONTINUOUS,
    .name = "Low-Power (Fast/Noisy)"
};

static const ina226_profile_t g_profile_dynamic = {
    .avg = INA226_AVG_16,
    .vshct = INA226_CONV_TIME_588US,
    .vbusct = INA226_CONV_TIME_588US,
    .mode = INA226_MODE_BOTH_CONTINUOUS,
    .name = "Dynamic (Balanced)"
};

static const ina226_profile_t g_profile_high_precision = {
    .avg = INA226_AVG_128,
    .vshct = INA226_CONV_TIME_2116US,
    .vbusct = INA226_CONV_TIME_2116US,
    .mode = INA226_MODE_BOTH_CONTINUOUS,
    .name = "High-Precision (Low-Noise)"
};

/* Імітація системного таймера (Systick) у мілісекундах */
static uint32_t g_sys_tick_ms = 0U;

/**
 * @brief Імітація отримання поточного часу в мс.
 */
static uint32_t get_system_tick_ms(void)
{
    return g_sys_tick_ms;
}

/**
 * @brief Обробник зовнішньої лінії ALERT від INA226 (EXTI Line ISR).
 */
void EXTI15_10_IRQHandler(void)
{
    /* Виклик обробника FSM драйвера при падінні рівня ALERT */
    // ina226_on_alert_interrupt(&ina_fsm);
}

/**
 * @brief Головна функція програми.
 */
int main(void)
{
    /* 1. Ініціалізація низькорівневої периферії I2C1 (100 кГц) */
    if (i2c1_init(100000U) != I2C_OK) {
        printf("[ERROR] Збій ініціалізації периферії I2C1!\n");
        return -1;
    }

    /* 2. Створення екземпляра кінцевого автомата INA226 */
    ina226_fsm_t ina_fsm;
    if (ina226_init(&ina_fsm, INA226_I2C_ADDR, SHUNT_RESISTOR_OHM, MAX_CURRENT_AMP) != INA226_OK) {
        printf("[ERROR] Збій ініціалізації давача INA226 (ID mismatch / I2C error)!\n");
        return -1;
    }

    printf("[INFO] INA226 ініціалізовано успішно. CAL=0x%04X, LSB=%.6f A\n", 
           ina_fsm.cal_val, ina_fsm.current_lsb_a);

    /* 3. Встановлення початкового базового профілю (Dynamic) */
    ina226_set_profile(&ina_fsm, &g_profile_dynamic);
    printf("[INFO] Активовано профіль: %s\n", ina_fsm.active_profile.name);

    uint32_t last_print_ms = 0;

    /* 4. Головний неблокуючий цикл */
    while (1) {
        /* Симуляція плину системного часу (1 крок = 1 мс) */
        g_sys_tick_ms++;

        /* Просування стану кінцевого автомата INA226 */
        ina226_fsm_process(&ina_fsm, get_system_tick_ms());

        /* Періодичний вивід зчитаних даних при завершенні вимірювального циклу */
        if (g_sys_tick_ms - last_print_ms >= 100U) {
            last_print_ms = g_sys_tick_ms;

            ina226_data_t *data = &ina_fsm.latest_data;
            printf("[TELEMETRY %lu ms] Vbus: %.3f V | Vshunt: %.3f mV | Current: %.3f A | Power: %.3f W\n",
                   (unsigned long)g_sys_tick_ms,
                   data->bus_voltage_v,
                   data->shunt_voltage_mv,
                   data->current_a,
                   data->power_w);

            /* Логіка динамічної зміни профілів конфігурації залежно від струму */
            if (data->current_a > 3.0f && ina_fsm.active_profile.avg != INA226_AVG_1) {
                printf("[ALERT] Високе навантаження! Перехід на профіль з високою швидкістю відгуку...\n");
                ina226_set_profile(&ina_fsm, &g_profile_low_power);
            } else if (data->current_a < 0.5f && ina_fsm.active_profile.avg != INA226_AVG_128) {
                printf("[INFO] Низьке навантаження. Перехід на профіль високої точності...\n");
                ina226_set_profile(&ina_fsm, &g_profile_high_precision);
            }
        }

        /* Симуляція обмеження швидкості циклу у реальній системі */
        if (g_sys_tick_ms > 5000U) {
            printf("[INFO] Демонстраційний цикл успішно завершено.\n");
            break;
        }
    }

    return 0;
}
