#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include "servo_pwm.h"
#include "encoder_reader.h"
#include "current_adc.h"

/**
 * @file main.c
 * @brief Головний тестовий модуль керування мікросервоприводом MG90S V2.
 *
 * Демонструє комплексне використання:
 * 1. Низькорівневого таймера ШІМ (50 Гц, 1000..2000 мкс).
 * 2. Декодування квадратурного енкодера з пригніченням брязкоту.
 * 3. Моніторингу струму через АЦП із виявленням пускового струму та захистом від заклинювання редуктора.
 */

int main(void)
{
    printf("===============================================================\n");
    printf("  Мікросервопривод MG90S V2: Тестовий C-модуль керування  \n");
    printf("===============================================================\n\n");

    /* 1. Ініціалізація ШІМ-таймера (вхідна частота таймера 16 МГц) */
    servo_pwm_config_t pwm_cfg = {
        .timer_clock_hz = 16000000U,
        .initial_pulse_us = SERVO_PULSE_CENTER_US,
        .invert_polarity = false
    };

    if (servo_pwm_init(&pwm_cfg) != 0) {
        printf("[ПОМИЛКА] Не вдалося ініціалізувати ШІМ-таймер!\n");
        return -1;
    }
    printf("[OK] ШІМ-таймер налаштовано: 50 Гц (період 20 мкс), початковий імпульс: %u мкс (%.1f deg)\n",
           servo_pwm_get_current_pulse_us(), servo_pwm_get_current_angle());

    /* 2. Ініціалізація декодера квадратурного енкодера (діапазон 0..100 кроків, крок 10 мкс) */
    encoder_state_t encoder;
    encoder_init(&encoder, 0, 100, 10);
    printf("[OK] Квадратурний енкодер ініціалізовано (крок імпульсу: %u мкс)\n", encoder.pulse_step_us);

    /* 3. Ініціалізація АЦП струмового моніторингу (alpha = 0.2, R_shunt = 0.1 Ом) */
    adc_current_monitor_t current_mon;
    current_adc_init(&current_mon, 0.2f, 0.1f);
    printf("[OK] АЦП моніторинг струму готовий (Шунт: %.2f Ом, Поріг заклинювання: %.0f мА)\n\n",
           current_mon.shunt_resistance_ohm, STALL_CURRENT_THRESHOLD_MA);

    printf("--- Етап 1: Симуляція обертання ручки енкодера (Зміна позиції вала) ---\n");
    
    /* Симуляція серії переходів фаз енкодера за годинниковою стрілкою */
    bool phase_a_sequence[] = { false, true,  true,  false, false, true,  true,  false };
    bool phase_b_sequence[] = { false, false, true,  true,  false, false, true,  true  };
    size_t num_events = sizeof(phase_a_sequence) / sizeof(phase_a_sequence[0]);

    uint32_t system_time_ms = 0;

    for (size_t i = 0; i < num_events; i++) {
        /* Обробка брязкоту потребує 3 послідовних стабільних відліків */
        for (int sample = 0; sample < 3; sample++) {
            encoder_update_pins(&encoder, phase_a_sequence[i], phase_b_sequence[i]);
        }

        uint16_t new_pulse = encoder_to_pulse_us(&encoder);
        float new_angle = encoder_to_angle_deg(&encoder);
        servo_pwm_set_pulse_us(new_pulse);

        /* Симуляція нормального струму споживання двигуна (~150 мА) */
        uint16_t sim_raw_adc = 186; /* ~15 мВ на 0.1 Ом -> 150 мА */
        current_adc_process_sample(&current_mon, sim_raw_adc, system_time_ms);

        printf("[%04u ms] Енкодер крок %zu | ШІМ: %u мкс | Кут: %5.1f deg | Струм: %5.1f мА | Статус: OK\n",
               system_time_ms, i + 1, new_pulse, new_angle, current_mon.filtered_current_ma);

        system_time_ms += 20;
    }

    printf("\n--- Етап 2: Симуляція пускового струму двигуна (Inrush Current transient) ---\n");
    
    /* Резкий старт сервопривода створює сплеск струму ~520 мА на 60 мс */
    for (int i = 0; i < 4; i++) {
        uint16_t inrush_adc = 645; /* ~64.5 мВ на 0.1 Ом -> ~520 мА */
        current_adc_process_sample(&current_mon, inrush_adc, system_time_ms);

        printf("[%04u ms] Пусковий сплеск | Сирий АЦП: %4u | Струм EMA: %5.1f мА | Статус Код: %d (INRUSH)\n",
               system_time_ms, current_mon.raw_adc_value, current_mon.filtered_current_ma, current_mon.status);

        system_time_ms += 20;
    }

    printf("\n--- Етап 3: Симуляція механічного заклинювання (Stall Detection) ---\n");
    
    /* Ручне примусове блокування вала MG90S V2: струм різко зростає до ~850 мА */
    uint16_t stall_adc = 1054; /* ~105.4 мВ на 0.1 Ом -> ~850 мА */

    for (int i = 0; i < 16; i++) {
        current_adc_process_sample(&current_mon, stall_adc, system_time_ms);

        bool is_stalled = current_adc_is_stall_detected(&current_mon);

        printf("[%04u ms] Заклинювання редуктора | Струм EMA: %5.1f мА | Статус Код: %d | Аварія: %s\n",
               system_time_ms, current_mon.filtered_current_ma, current_mon.status,
               is_stalled ? "ТАК (FAULТ!)" : "НІ (WARNING)");

        if (is_stalled) {
            printf("\n[УВАГА] БЕЗПЕКОВА РЕАКЦІЯ: Зняття живлення з ШІМ-виходу для захисту редуктора!\n");
            servo_pwm_enable(false);
            break;
        }

        system_time_ms += 20;
    }

    printf("\n--- Етап 4: Скидання аварії після усунення перешкоди ---\n");
    current_adc_reset_fault(&current_mon);
    servo_pwm_enable(true);
    
    /* Нормалізація струму */
    uint16_t normal_adc = 186;
    current_adc_process_sample(&current_mon, normal_adc, system_time_ms);

    printf("[%04u ms] Відновлення роботи | ШІМ: %u мкс | Струм: %5.1f мА | Статус Код: %d (OK)\n",
           system_time_ms, servo_pwm_get_current_pulse_us(), current_mon.filtered_current_ma, current_mon.status);

    printf("\n===============================================================\n");
    printf("  Тестування C-модуля MG90S V2 успішно завершено!  \n");
    printf("===============================================================\n");

    return 0;
}
