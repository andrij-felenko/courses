#ifndef RVDT_RDC_H
#define RVDT_RDC_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/// Маски статусних бітів аварій RDC-конвертера
#define RDC_STATUS_DOS_MASK   (1U << 0) ///< Loss of Signal (Втрата корисного сигналу RVDT)
#define RDC_STATUS_LOS_MASK   (1U << 1) ///< Degradation of Signal (Деградація/асиметрія сигналу)
#define RDC_STATUS_LOT_MASK   (1U << 2) ///< Loss of Tracking (Втрата стеження скінченного автомата RDC)
#define RDC_STATUS_PARITY_MASK (1U << 7) ///< Парність каду SPI

/// Коди статусів обробки каналу RVDT
typedef enum {
    RVDT_OK = 0,               ///< Успішне вичитання даних
    RVDT_ERR_SPI_TIMEOUT,      ///< Таймаут апаратного інтерфейсу SPI
    RVDT_ERR_LOSS_OF_SIGNAL,   ///< Аварія LOS: обрив або КЗ обмотки давача RVDT
    RVDT_ERR_SIGNAL_DEGRADED,  ///< Аварія DOS: вихід амплітуди за межі допуску
    RVDT_ERR_TRACKING_LOST,    ///< Аварія LOT: перевищення допустимої кутової швидкості
    RVDT_ERR_PARITY            ///< Помилка контроля парності SPI
} rvdt_status_t;

/// Розрядність перетворення RDC-конвертера
typedef enum {
    RDC_RES_10_BIT = 10,
    RDC_RES_12_BIT = 12,
    RDC_RES_14_BIT = 14,
    RDC_RES_16_BIT = 16
} rdc_resolution_t;

/// Конфігураційна структура вимірювального каналу RVDT
typedef struct {
    uint8_t spi_channel;            ///< Номер апаратного каналу SPI
    rdc_resolution_t resolution;    ///< Обрана розрядність RDC (10, 12, 14 або 16 біт)
    float zero_offset_deg;          ///< Кутовий зсув електричного нуля в градусах
    float sensitivity_mv_per_deg;   ///< Чутливість RVDT [мВ/град]
    uint32_t timeout_us;            ///< Максимальний таймаут SPI-транзакції у мікросекундах
} rvdt_config_t;

/// Вихідні виміряні дані RVDT
typedef struct {
    uint16_t raw_code;              ///< Сирий 16-бітний двійковий код з RDC
    float angle_deg;                ///< Розрахований кут у фізичних градусах [-180.0 .. +180.0]
    float angle_rad;                ///< Розрахований кут у радіанах [-π .. +π]
    uint8_t rdc_status_flags;       ///< Прапорці статусних регістрів RDC (LOS, DOS, LOT)
    rvdt_status_t driver_status;    ///< Загальний статус обробки драйвером
} rvdt_measurement_t;

/// Тип вказівника на функцію низькорівневої SPI-транзакції мікроконтролера
typedef bool (*rvdt_spi_transfer_fn)(uint8_t spi_ch, const uint8_t *tx_buf, uint8_t *rx_buf, uint16_t len, uint32_t timeout_us);

/// Контекст екземпляра драйвера RVDT
typedef struct {
    rvdt_config_t config;
    rvdt_spi_transfer_fn spi_transfer;
    bool is_initialized;
} rvdt_handle_t;

/**
 * @brief Ініціалізація екземпляра драйвера RVDT/RDC
 * @param handle Вказівник на контекст драйвера
 * @param config Конфігураційні параметри каналу
 * @param spi_fn Вказівник на низькорівневу функцію передачі SPI
 * @return rvdt_status_t Результат ініціалізації
 */
rvdt_status_t rvdt_init(rvdt_handle_t *handle, const rvdt_config_t *config, rvdt_spi_transfer_fn spi_fn);

/**
 * @brief Зчитування каду RDC, аналіз аварій та перерахунок кута RVDT
 * @param handle Вказівник на контекст драйвера
 * @param result Вказівник на структуру вихідних даних
 * @return rvdt_status_t Статус результату зчитування
 */
rvdt_status_t rvdt_read_angle(rvdt_handle_t *handle, rvdt_measurement_t *result);

#ifdef __cplusplus
}
#endif

#endif // RVDT_RDC_H
