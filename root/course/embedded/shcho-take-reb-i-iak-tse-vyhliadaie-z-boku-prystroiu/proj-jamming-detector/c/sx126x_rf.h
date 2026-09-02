#ifndef SX126X_RF_H
#define SX126X_RF_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "ew_detector.h"

typedef enum {
    SX126X_OK = 0,
    SX126X_ERR_ARG,   /* порожній вказівник */
    SX126X_ERR_BUSY,  /* мікросхема не відпустила лінію BUSY */
    SX126X_ERR_SPI    /* обмін по SPI не відбувся */
} sx126x_status_t;

/* Гачки плати. Обмін — повний дуплекс однією транзакцією, NSS тримає саме
   ця функція; wait_busy чекає спаду лінії BUSY трансивера. */
bool     sx126x_bsp_xfer(const uint8_t *tx, uint8_t *rx, size_t len);
bool     sx126x_bsp_wait_busy(uint32_t timeout_us);
uint32_t sx126x_bsp_now_ms(void);

/* Знімає одну вибірку телеметрії: миттєвий RSSI, SNR останнього кадру,
   прапорці преамбули й CRC, відновлений стан підсилення. Поля timestamp_ms
   заповнює сам драйвер, throttle_pct лишається на виклику. */
sx126x_status_t sx126x_read_sample(ew_rf_sample_t *out);

#endif /* SX126X_RF_H */
