#ifndef IMU_FIFO_API_H
#define IMU_FIFO_API_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Режими роботи апаратного FIFO */
typedef enum {
    IMU_FIFO_MODE_BYPASS       = 0x00, /* FIFO вимкнено */
    IMU_FIFO_MODE_STREAM       = 0x01, /* Потоковий режим із витісненням старих даних */
    IMU_FIFO_MODE_STOP_ON_FULL = 0x02  /* Зупинка запису при 100% заповненні */
} imu_fifo_mode_t;

/* Статус виконання операцій драйвера */
typedef enum {
    IMU_OK                 = 0,
    IMU_ERR_NULL_PTR       = -1,
    IMU_ERR_BUS_FAIL       = -2,
    IMU_ERR_FIFO_OVERFLOW  = -3,
    IMU_ERR_FRAME_SYNC     = -4,
    IMU_ERR_TIMEOUT        = -5,
    IMU_ERR_INVALID_PARAM  = -6
} imu_status_t;

/* Розпакований фізичний кадр інерційних вимірювань у системі СІ */
typedef struct {
    float    accel_mps2[3];    /* Лінійне прискорення [X, Y, Z] у м/с² */
    float    gyro_radps[3];    /* Кутова швидкість [X, Y, Z] у рад/с */
    float    temp_celsius;     /* Температура кристала в °C */
    uint32_t timestamp_us;     /* Апаратний таймстемп у мікросекундах */
    bool     has_accel;        /* Прапорець валідності даних акселерометра */
    bool     has_gyro;         /* Прапорець валідності даних гіроскопа */
    bool     fsync_event;      /* Прапорець події зовнішньої кадрової мітки */
} imu_sample_t;

/* Параметри конфігурації FIFO */
typedef struct {
    imu_fifo_mode_t mode;              /* Режим буферизації */
    uint16_t        watermark_bytes;   /* Поріг Watermark у байтах (наприклад, 160 Б) */
    bool            enable_accel;      /* Дозвіл запису акселерометра */
    bool            enable_gyro;       /* Дозвіл запису гіроскопа */
    bool            enable_timestamp;  /* Дозвіл запису апаратного таймстемпа */
    bool            enable_hires_20bit;/* Режим підвищеної розрядності (Packet 4) */
} imu_fifo_config_t;

/* Ініціалізація сенсора та конфігурація буфера FIFO */
imu_status_t imu_fifo_init(const imu_fifo_config_t *config);

/* Очищення буфера та обнулення покажчиків Head/Tail (FIFO Flush) */
imu_status_t imu_fifo_flush(void);

/* Отримання поточної кількості незчитаних байтів у буфері FIFO */
imu_status_t imu_fifo_get_count(uint16_t *out_byte_count);

/* Пакетне вичитування сирого масиву байтів через SPI (сумісне з DMA) */
imu_status_t imu_fifo_read_burst(uint8_t *rx_buf, uint16_t length);

/* Потоковий парсер сирого буфера в масив фізичних відліків imu_sample_t */
imu_status_t imu_fifo_parse_frames(
    const uint8_t *raw_stream,
    size_t         raw_bytes,
    imu_sample_t  *out_samples,
    size_t         max_samples,
    size_t        *parsed_count
);

#ifdef __cplusplus
}
#endif

#endif /* IMU_FIFO_API_H */
