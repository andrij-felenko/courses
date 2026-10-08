#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include "water_flow_sensor.h"
#include "power_down_eeprom.h"
#include "mqtt_telemetry.h"

/**
 * @file main.c
 * @brief Головний модуль ембеддед-додатка обліку водоспоживання.
 */

int main(void) {
    printf("=== Ініціалізація системи обліку витрати води (G1/2\" Hall Sensor) ===\n");

    /* 1. Налаштування та ініціалізація модуля PVD / EEPROM */
    power_down_config_t pd_cfg = {
        .eeprom_address = 0x0010,
        .vcc_threshold_mv = 2900 /* Спрацьовування при просіданні живлення нижче 2.9 В */
    };
    
    if (!power_down_eeprom_init(&pd_cfg)) {
        printf("[ERROR] Не вдалося ініціалізувати модуль Power-Down EEPROM!\n");
        return 1;
    }

    /* 2. Спроба відновлення накопиченого об'єму з EEPROM під час старт-апу */
    double restored_volume = 0.0;
    uint64_t restored_pulses = 0;
    if (power_down_eeprom_restore(&restored_volume, &restored_pulses)) {
        printf("[EEPROM] Успішно відновлено показники: %.3f л (%llu імпульсів)\n",
               restored_volume, (unsigned long long)restored_pulses);
    } else {
        printf("[EEPROM] Записів не знайдено або CRC некоректний. Старт з 0.0 л.\n");
    }

    /* 3. Конфігурація та ініціалізація драйвера давача витрати води */
    water_flow_config_t flow_cfg = {
        .k_factor = 7.5f,              /* Паспортний K-фактор давача G1/2": 7.5 Гц / (л/хв) */
        .sample_period_ms = 500,       /* Розрахунковий інтервал: 500 мс */
        .min_flow_cutoff_lpm = 0.15f,  /* Відсікання шумів менше 0.15 л/хв */
        .exti_gpio_pin = 4             /* GPIO 4 підключено до виходу Холла */
    };

    if (!water_flow_sensor_init(&flow_cfg)) {
        printf("[ERROR] Помилка ініціалізації давача витрати води!\n");
        return 1;
    }

    /* Встановлення відновлених з EEPROM даних */
    water_flow_sensor_set_total_volume(restored_volume, restored_pulses);

    /* 4. Ініціалізація MQTT телеметрії */
    if (!mqtt_telemetry_init("water_meter_01", "192.168.1.50", 1883)) {
        printf("[ERROR] Помилка налаштування MQTT телеметрії!\n");
        return 1;
    }

    printf("=== Драйвер повністю готовий до роботи. Запуск головного циклу ===\n");

    uint32_t system_time_ms = 0;
    uint32_t system_time_us = 0;
    uint32_t last_telemetry_time_ms = 0;

    /* Моделювання роботи системи протягом 5 секунд */
    for (int step = 0; step < 10; step++) {
        system_time_ms += 500;
        system_time_us += 500000;

        /* Моделювання надходження імпульсів від турбіни з елементом Холла (витрата ~6 л/хв => f = 45 Гц) */
        /* При f = 45 Гц кожні 22.2 мс приходить імпульс */
        for (int p = 0; p < 22; p++) {
            uint32_t pulse_time_us = system_time_us - 500000 + (p * 22222);
            water_flow_sensor_on_pulse_isr(pulse_time_us);
        }

        /* Періодична неблокуюча обробка метрик за таймером */
        water_flow_sensor_process_timer_tick(system_time_ms);

        /* Періодична відправка MQTT телеметрії кожні 1000 мс */
        if (system_time_ms - last_telemetry_time_ms >= 1000) {
            last_telemetry_time_ms = system_time_ms;
            water_flow_metrics_t metrics;
            water_flow_sensor_get_metrics(&metrics);
            
            printf("[STATUS %u ms] Частота: %.2f Гц | Витрата: %.2f л/хв | Всього: %.4f л\n",
                   system_time_ms, metrics.pulse_frequency_hz, metrics.flow_rate_lpm, metrics.total_volume_liters);

            mqtt_telemetry_send_flow_report(&metrics, true);
        }
    }

    /* Моделювання аварійної події знеструмлення (Power-Down) */
    printf("\n[WARNING] Спрацювання детектора PVD (просідання напруги VCC < 2.9 В)!\n");
    power_down_pvd_isr();

    /* Моделювання перезавантаження MCU та перевірки відновлення даних */
    printf("\n=== Симуляція перезавантаження мікроконтролера ===\n");
    double reboot_volume = 0.0;
    uint64_t reboot_pulses = 0;
    if (power_down_eeprom_restore(&reboot_volume, &reboot_pulses)) {
        printf("[EEPROM RESTORE] Показники успішно відновлено після старт-апу: %.4f л (%llu імпульсів)\n",
               reboot_volume, (unsigned long long)reboot_pulses);
    } else {
        printf("[ERROR] Не вдалося відновити дані після аварійного збереження!\n");
    }

    return 0;
}
