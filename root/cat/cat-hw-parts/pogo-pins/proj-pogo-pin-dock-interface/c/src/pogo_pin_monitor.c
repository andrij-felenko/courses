/**
 * @file pogo_pin_monitor.c
 * @brief Реалізація алгоритму детектування мікророзривів контактів Pogo Pin.
 */

#include "pogo_pin_monitor.h"
#include <stdio.h>
#include <string.h>

void pogo_monitor_init(pogo_monitor_t *monitor, const pogo_config_t *config) {
    if (!monitor) return;

    if (config) {
        monitor->config = *config;
    } else {
        monitor->config.min_glitch_duration_us = 5;      // 5 мкс мінімальний поріг
        monitor->config.debounce_filter_us = 1;          // 1 мкс шумовий фільтр
        monitor->config.sampling_period_ms = 10;
    }

    memset(&monitor->stats, 0, sizeof(pogo_stats_t));
    monitor->current_contact_state = true; // За замовчуванням контакт притиснутий
    monitor->last_transition_timestamp_us = 0;
}

void pogo_monitor_handle_edge(pogo_monitor_t *monitor, bool pin_state, uint32_t current_timestamp_us) {
    if (!monitor) return;

    // Якщо стан не змінився, ігноруємо
    if (monitor->current_contact_state == pin_state) return;

    uint32_t delta_us = 0;
    if (current_timestamp_us >= monitor->last_transition_timestamp_us) {
        delta_us = current_timestamp_us - monitor->last_transition_timestamp_us;
    } else {
        // Переповнення 32-бітного лічильника мікросекунд
        delta_us = (UINT32_MAX - monitor->last_transition_timestamp_us) + current_timestamp_us + 1;
    }

    // Перехід із розімкненого стану (false) у замкнений (true): кінець мікророзриву
    if (pin_state && !monitor->current_contact_state) {
        if (delta_us >= monitor->config.min_glitch_duration_us) {
            monitor->stats.contact_open_events++;
            monitor->stats.total_downtime_us += delta_us;
            if (delta_us > monitor->stats.max_glitch_duration_us) {
                monitor->stats.max_glitch_duration_us = delta_us;
            }
        }
    }

    monitor->current_contact_state = pin_state;
    monitor->last_transition_timestamp_us = current_timestamp_us;
}

void pogo_monitor_update_stats(pogo_monitor_t *monitor, uint32_t total_test_duration_ms) {
    if (!monitor || total_test_duration_ms == 0) return;

    uint64_t total_test_duration_us = (uint64_t)total_test_duration_ms * 1000ULL;
    if (total_test_duration_us > 0) {
        monitor->stats.contact_loss_percent = ((double)monitor->stats.total_downtime_us / (double)total_test_duration_us) * 100.0;
    }
}

void pogo_monitor_print_report(const pogo_monitor_t *monitor) {
    if (!monitor) return;

    printf("\n======================================================\n");
    printf("   ДІАГНОСТИЧНИЙ ЗВІТ СТАБІЛЬНОСТІ КОНТАКТУ POGO PIN   \n");
    printf("======================================================\n");
    printf(" Зафіксовано подій розриву     : %u\n", monitor->stats.contact_open_events);
    printf(" Сумарний час розриву          : %u мкс\n", monitor->stats.total_downtime_us);
    printf(" Максимальна тривалість збою   : %u мкс\n", monitor->stats.max_glitch_duration_us);
    printf(" Відсоток втрати контакту      : %.4f %%\n", monitor->stats.contact_loss_percent);
    printf("------------------------------------------------------\n");
    printf(" ОЦІНКА ВІБРОСТІЙКОСТІ ТА ФРЕТИНГ-ЗНОСУ:\n");

    if (monitor->stats.contact_open_events == 0) {
        printf(" [ІДЕАЛЬНО] Розривів не виявлено. Притиск пружини стабільний,\n");
        printf(" контактний опір у межах норми.\n");
    } else if (monitor->stats.contact_loss_percent < 0.05) {
        printf(" [ДОПУСТИМО] Зафіксовано одиничні мікророзриви від вібрації.\n");
        printf(" Контакт придатний для передачі живлення, але чутливий для швидкісних шин.\n");
    } else {
        printf(" [КРИТИЧНО] Висока частота розмикань контакту!\n");
        printf(" Ознака просідання пружини, фретингу або недостатнього робочого ходу.\n");
    }
    printf("======================================================\n");
}
