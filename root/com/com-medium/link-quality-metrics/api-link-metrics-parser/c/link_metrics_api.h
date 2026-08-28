/* link_metrics_api.h - C API структури даних та функції розбору метрик */
#ifndef LINK_METRICS_API_H
#define LINK_METRICS_API_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    LINK_HEALTH_CRITICAL = 0,
    LINK_HEALTH_DEGRADED = 1,
    LINK_HEALTH_GOOD     = 2,
    LINK_HEALTH_EXCELLENT= 3
} link_health_t;

typedef struct {
    int16_t rssi_dbm_x10;    /* RSSI у децибел-міліватах * 10 (-1200 .. 0) */
    int16_t snr_db_x10;      /* SNR у децибелах * 10 (-200 .. +400) */
    uint8_t lqi;             /* Апаратний LQI (0 .. 255) */
    uint16_t per_permille;   /* PER у проміле (0 = 0.0%, 1000 = 100.0%) */
    link_health_t health;    /* Класифікований стан */
} radio_link_metrics_t;

typedef struct {
    uint32_t rx_success_count;
    uint32_t rx_crc_error_count;
    uint32_t rx_timeout_count;
    radio_link_metrics_t current_metrics;
} link_stats_report_t;

/**
 * @brief Ініціалізація структури звіту метрик.
 * @param report Вказівник на структуру звіту.
 */
void link_metrics_init(link_stats_report_t *report);

/**
 * @brief Оновлення метрик при отриманні нового кадру.
 * @param report Вказівник на структуру звіту.
 * @param raw_rssi_x10 Сирий RSSI у 0.1 дБм.
 * @param raw_snr_x10 Сирий SNR у 0.1 дБ.
 * @param raw_lqi Апаратне значення LQI (0..255).
 * @param crc_passed Прапор успішного перевірочного коду CRC.
 */
void link_metrics_update_frame(link_stats_report_t *report,
                               int16_t raw_rssi_x10,
                               int16_t raw_snr_x10,
                               uint8_t raw_lqi,
                               bool crc_passed);

/**
 * @brief Форматування телеметричного рядка звіту у буфер JSON.
 * @param report Вказівник на структуру звіту.
 * @param buf Буфер для запису текстового рядка.
 * @param buf_len Максимальна довжина буфера у байтах.
 * @return Кількість записаних байтів або -1 при помилці.
 */
int link_metrics_to_json(const link_stats_report_t *report, char *buf, size_t buf_len);

#ifdef __cplusplus
}
#endif

#endif /* LINK_METRICS_API_H */
