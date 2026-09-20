#include <stdio.h>
#include "apc_laser_controller.h"

/**
 * @file main.c
 * @brief Демонстраційний приклад використання драйвера APC лазерного діода.
 */

/* Імітація апаратних ресурсів мікроконтролера */
static uint16_t g_simulated_dac_val = 0;
static bool g_simulated_enable = false;
static bool g_simulate_overcurrent = false;

/* Перевизначення низькорівневих апаратних функцій для тестування */

void hal_gpio_write_pin(uint8_t port, uint16_t pin, bool state) {
    (void)port;
    (void)pin;
    g_simulated_enable = state;
    printf("  [HAL GPIO] Лінія Enable переключена в стан: %s\n", state ? "HIGH (Увімкнено)" : "LOW (Вимкнено)");
}

void hal_dac_write_value(uint8_t channel, uint16_t raw_val) {
    (void)channel;
    g_simulated_dac_val = raw_val;
    printf("  [HAL DAC] Встановлено нове значення ЦАП: %u LSB\n", raw_val);
}

uint16_t hal_adc_read_value(uint8_t channel) {
    (void)channel;
    if (g_simulate_overcurrent) {
        /* Штучне імітування перевищення струму фотодіода */
        return 3800;
    }
    if (!g_simulated_enable) {
        return 0;
    }
    /* Лінійна модель оптичного відгуку фотодіода від струму накачки ЦАП */
    return (uint16_t)((g_simulated_dac_val * 75) / 100);
}

void hal_delay_ms(uint32_t ms) {
    (void)ms;
}

int main(void) {
    printf("=== Демонстрація системи керування лазерним діодом (APC) ===\n\n");

    apc_driver_t laser;
    apc_config_t config = {
        .hw = {
            .dac_channel = 1,
            .adc_pd_channel = 0,
            .gpio_enable_port = 1,
            .gpio_enable_pin = 5
        },
        .max_pd_adc_raw = 3500,       /* Поріг захисту по АЦП фотодіода */
        .target_pd_adc_raw = 2000,    /* Початкова цільова потужність */
        .dac_max_limit = 3200,        /* Граничний струм накачки */
        .soft_start_step = 300,       /* Крок регулятора при плавному пуску */
        .soft_start_delay_ms = 10,    /* Пауза між кроками пуску */
        .kp_gain = 6,                 /* Коефіцієнт P-регулятора */
        .ki_gain = 2                  /* Коефіцієнт I-регулятора */
    };

    /* 1. Ініціалізація периферії та драйвера */
    printf("1. Ініціалізація драйвера...\n");
    apc_status_t status = apc_laser_init(&laser, &config);
    if (status != APC_OK) {
        printf("Помилка ініціалізації: %d\n", status);
        return 1;
    }

    /* 2. Виконання плавного пуску (Soft Start) */
    printf("\n2. Виконання плавного пуску (Soft Start)...\n");
    status = apc_laser_soft_start(&laser);
    if (status != APC_OK) {
        printf("Помилка плавного пуску: %d\n", status);
        return 1;
    }
    printf("Плавний пуск завершено. Стан драйвера: %d, ЦАП: %u LSB, Фотодіод АЦП: %u LSB\n",
           apc_laser_get_state(&laser), laser.current_dac_val, laser.last_adc_raw);

    /* 3. Цикл автоматичного регулювання потужності (APC) */
    printf("\n3. Робота суперциклу з регулюванням потужності APC...\n");
    for (int step = 1; step <= 4; step++) {
        status = apc_laser_update_apc(&laser);
        printf("  Крок APC %d: ЦАП = %u, АЦП фотодіода = %u, Помилка = %d\n",
               step, laser.current_dac_val, laser.last_adc_raw, status);
    }

    /* 4. Зміна установки цільової потужності */
    printf("\n4. Встановлення нового цільового рівня оптичної потужності (2400 LSB)...\n");
    apc_laser_set_target(&laser, 2400);
    for (int step = 1; step <= 3; step++) {
        apc_laser_update_apc(&laser);
        printf("  Оновлення %d: ЦАП = %u, АЦП фотодіода = %u\n",
               step, laser.current_dac_val, laser.last_adc_raw);
    }

    /* 5. Перевірка спрацьовування програмного захисту при аномалії */
    printf("\n5. Симуляція фотоструму вище безпечної межі (Аварія)...\n");
    g_simulate_overcurrent = true;
    status = apc_laser_update_apc(&laser);

    if (status == APC_ERROR_OVERCURRENT) {
        printf("  -> АВАРІЯ! Спрацював захист за струмом фотодіода.\n");
        printf("  -> Поточний стан: %d (APC_STATE_FAULT)\n", apc_laser_get_state(&laser));
        printf("  -> Стан сигналу Enable: %s, ЦАП: %u LSB\n",
               g_simulated_enable ? "HIGH" : "LOW", g_simulated_dac_val);
    }

    /* 6. Безпечне завершення роботи */
    apc_laser_disable(&laser);
    printf("\n=== Роботу контролера завершено ===\n");

    return 0;
}
