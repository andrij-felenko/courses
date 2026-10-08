/**
 * @file main.c
 * @brief Головний модуль програми керування енергоефективною системою з давачем HC-SR505.
 *
 * Демонструє повний цикл роботи: ініціалізація периферії, запуск режиму глибокого сну,
 * обробка апаратного переривання EXTI при виявленні руху, увімкнення навантаження через MOSFET,
 * проходження таймауту утримання та безпечне повернення МК в енергозберігаючий стан.
 */

#include "hc_sr505.h"
#include "mcu_power_exti.h"
#include <stdio.h>

/* Глобальний екземпляр драйвера давача HC-SR505 */
static hc_sr505_t g_pir_device;

/**
 * @brief Апаратний C-callback обробника переривань (EXTI ISR).
 */
static void pir_exti_isr_handler(void)
{
    /* Викликається безпосередньо з апаратного обробника переривань */
    hc_sr505_on_motion_isr(&g_pir_device);
}

int main(void)
{
    printf("===============================================================\n");
    printf("  Драйвер HC-SR505 — Мініатюрний PIR-давач руху (C / Low-Power)  \n");
    printf("===============================================================\n\n");

    /* 1. Ініціалізація апаратного рівня абстракції (HAL) */
    if (!mcu_gpio_init_pir_input()) {
        printf("Помилка ініціалізації вхідного GPIO для HC-SR505!\n");
        return -1;
    }

    if (!mcu_gpio_init_mosfet_output()) {
        printf("Помилка ініціалізації вихідного GPIO затвора MOSFET!\n");
        return -1;
    }

    /* 2. Конфігурація драйвера HC-SR505 */
    hc_sr505_config_t pir_cfg = {
        .active_hold_ms = 3000U,        /* Навантаження залишається увімкненим 3 сек після падіння сигналу */
        .cooldown_ms = 1500U,           /* Пауза стабілізації 1.5 сек перед глибоким сном */
        .auto_sleep_enable = false,     /* Авто-сон керується явним циклом для демонстрації */
        .active_high_logic = true       /* Сигнал 3.3V означає виявлення руху */
    };

    if (hc_sr505_init(&g_pir_device, &pir_cfg) != HC_SR505_OK) {
        printf("Помилка ініціалізації драйвера HC-SR505!\n");
        return -1;
    }

    /* 3. Реєстрація апаратного переривання EXTI (Rising Edge) */
    if (!mcu_exti_init_pir_interrupt(pir_exti_isr_handler)) {
        printf("Помилка конфігурації EXTI переривання!\n");
        return -1;
    }

    printf("Периферія успішно ініціалізована.\n");
    printf("Поточний стан системи: %s\n\n", hc_sr505_state_to_str(hc_sr505_get_state(&g_pir_device)));

    /* --- СЦЕНАРІЙ 1: Початок роботи, перехід системи у стан очікування руху (Deep Sleep) --- */
    printf("--- Сценарій 1: Вхід у режим глибокого сну --- \n");
    mcu_power_enter_deep_sleep();

    /* --- СЦЕНАРІЙ 2: Виявлення руху, апаратне прокидання та активація MOSFET --- */
    printf("\n--- Сценарій 2: Виявлення інфрачервоного руху --- \n");
    mcu_simulate_pir_hardware_event(true);

    /* Обробка стану машиною станів у головному циклі після пробудження */
    hc_sr505_process(&g_pir_device, mcu_get_tick_ms());

    printf(" Стан після ISR: %s\n", hc_sr505_state_to_str(hc_sr505_get_state(&g_pir_device)));
    printf(" Стан затвора MOSFET: %s (Потенціал V_GS подано)\n",
           g_pir_device.mosfet_gate_active ? "HIGH (ON)" : "LOW (OFF)");
    printf(" Лічильник спрацьовувань руху: %u\n", (unsigned int)g_pir_device.motion_trigger_count);

    /* Симуляція проходження часу активності HC-SR505 (~8 секунд тримає HIGH) */
    printf("\n--- Сценарій 3: Активна фаза присутності (HC-SR505 утримує HIGH) --- \n");
    for (int i = 1; i <= 3; i++) {
        mcu_delay_ms(1000);
        hc_sr505_process(&g_pir_device, mcu_get_tick_ms());
        printf(" t = %u мс | Сигнал OUT: %s | MOSFET: %s | Стан: %s\n",
               (unsigned int)mcu_get_tick_ms(),
               g_pir_device.motion_raw_signal ? "HIGH" : "LOW",
               g_pir_device.mosfet_gate_active ? "ON" : "OFF",
               hc_sr505_state_to_str(hc_sr505_get_state(&g_pir_device)));
    }

    /* --- СЦЕНАРІЙ 4: Припинення руху, зняття сигналу OUT та затримка активності --- */
    printf("\n--- Сценарій 4: Об'єкт залишив зону, сигнал OUT падає в LOW --- \n");
    mcu_simulate_pir_hardware_event(false);
    hc_sr505_read_raw_pin(&g_pir_device, &g_pir_device.motion_raw_signal);

    /* Проходження таймауту hold_ms (3000 мс) */
    while (hc_sr505_get_state(&g_pir_device) == PIR_STATE_LOAD_ACTIVE) {
        mcu_delay_ms(1000);
        hc_sr505_process(&g_pir_device, mcu_get_tick_ms());
        printf(" t = %u мс | Навантаження досі активне, зачекайте... | Стан: %s\n",
               (unsigned int)mcu_get_tick_ms(),
               hc_sr505_state_to_str(hc_sr505_get_state(&g_pir_device)));
    }

    /* --- СЦЕНАРІЙ 5: Завершення active_hold_ms, вимкнення MOSFET та Cooldown --- */
    printf("\n--- Сценарій 5: Вимкнення MOSFET та період стабілізації (Cooldown) --- \n");
    printf(" Стан затвора MOSFET: %s (V_GS знято)\n",
           g_pir_device.mosfet_gate_active ? "HIGH (ON)" : "LOW (OFF)");

    while (hc_sr505_get_state(&g_pir_device) == PIR_STATE_COOLDOWN) {
        mcu_delay_ms(500);
        hc_sr505_process(&g_pir_device, mcu_get_tick_ms());
        printf(" t = %u мс | Стабілізація... | Стан: %s\n",
               (unsigned int)mcu_get_tick_ms(),
               hc_sr505_state_to_str(hc_sr505_get_state(&g_pir_device)));
    }

    /* --- СЦЕНАРІЙ 6: Повернення в IDLE та Deep Sleep --- */
    printf("\n--- Сценарій 6: Систему повернуто у стан очікування --- \n");
    printf(" Остаточний стан: %s\n", hc_sr505_state_to_str(hc_sr505_get_state(&g_pir_device)));
    mcu_power_enter_deep_sleep();

    printf("\nДемонстрацію роботи драйвера HC-SR505 успішно завершено.\n");
    return 0;
}
