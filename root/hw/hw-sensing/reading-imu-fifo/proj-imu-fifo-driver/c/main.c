#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ICM42688_REG_DEVICE_CONFIG   0x11
#define ICM42688_REG_INT_CONFIG      0x14
#define ICM42688_REG_FIFO_CONFIG     0x16
#define ICM42688_REG_INT_STATUS      0x2D
#define ICM42688_REG_FIFO_COUNTH     0x2E
#define ICM42688_REG_FIFO_COUNTL     0x2F
#define ICM42688_REG_FIFO_DATA       0x30
#define ICM42688_REG_SIGNAL_PATH_RESET 0x4B
#define ICM42688_REG_PWR_MGMT0       0x4E
#define ICM42688_REG_GYRO_CONFIG0    0x4F
#define ICM42688_REG_ACCEL_CONFIG0   0x50
#define ICM42688_REG_FIFO_CONFIG1    0x5F
#define ICM42688_REG_FIFO_CONFIG2    0x60
#define ICM42688_REG_FIFO_CONFIG3    0x61

#define FIFO_FRAME_HEADER_ACCEL_BIT  0x40
#define FIFO_FRAME_HEADER_GYRO_BIT   0x20
#define FIFO_FRAME_HEADER_TIMESTAMP_BIT 0x02
#define FIFO_FRAME_EMPTY_MARKER      0x80

#define WATERMARK_FRAME_COUNT        10
#define PACKET_SIZE_BYTES            16
#define DMA_BURST_BUFFER_SIZE        (WATERMARK_FRAME_COUNT * PACKET_SIZE_BYTES)

/* Чутливість: ±16g для акселерометра, ±2000 dps для гіроскопа */
#define ACCEL_SCALE_FACTOR_16G       (16.0f / 32768.0f * 9.80665f) /* м/с² */
#define GYRO_SCALE_FACTOR_2000DPS    (2000.0f / 32768.0f * 0.0174532925f) /* рад/с */

typedef struct {
    float accel[3];
    float gyro[3];
    float temperature;
    uint32_t timestamp_us;
} imu_packet_t;

/* Структура драйвера */
typedef struct {
    uint8_t dma_rx_buf_ping[DMA_BURST_BUFFER_SIZE + 1];
    uint8_t dma_rx_buf_pong[DMA_BURST_BUFFER_SIZE + 1];
    uint8_t dma_tx_dummy[DMA_BURST_BUFFER_SIZE + 1];
    volatile bool active_buffer_is_pong;
    volatile bool dma_in_progress;
    volatile bool data_ready_for_processing;
    uint16_t last_fifo_count;
} imu_driver_t;

static imu_driver_t g_imu_drv;

/* Апаратні абстракції платформи (реалізуються для конкретного MCU) */
extern void platform_spi_write_reg(uint8_t reg, uint8_t val);
extern uint8_t platform_spi_read_reg(uint8_t reg);
extern void platform_spi_start_dma(const uint8_t *tx, uint8_t *rx, uint16_t len);
extern void platform_delay_ms(uint32_t ms);

/* Ініціалізація сенсора та конфігурація буфера FIFO */
void imu_init_fifo_pipeline(void) {
    memset(&g_imu_drv, 0, sizeof(imu_driver_t));
    g_imu_drv.dma_tx_dummy[0] = ICM42688_REG_FIFO_DATA | 0x80; /* SPI Read command */

    /* 1. Скидання пристрою */
    platform_spi_write_reg(ICM42688_REG_DEVICE_CONFIG, 0x01);
    platform_delay_ms(10);

    /* 2. Увімкнення датчиків: Акселерометр + Гіроскоп у Low-Noise Mode */
    platform_spi_write_reg(ICM42688_REG_PWR_MGMT0, 0x0F);
    platform_delay_ms(50);

    /* 3. Встановлення діапазонів та ODR = 1000 Гц */
    platform_spi_write_reg(ICM42688_REG_ACCEL_CONFIG0, 0x06); /* ±16g, 1 kHz */
    platform_spi_write_reg(ICM42688_REG_GYRO_CONFIG0, 0x06);  /* ±2000 dps, 1 kHz */

    /* 4. Скидання покажчиків FIFO */
    platform_spi_write_reg(ICM42688_REG_SIGNAL_PATH_RESET, 0x02);
    platform_delay_ms(2);

    /* 5. Налаштування порогу Watermark (160 байтів) */
    uint16_t wm_bytes = DMA_BURST_BUFFER_SIZE;
    platform_spi_write_reg(ICM42688_REG_FIFO_CONFIG2, (uint8_t)(wm_bytes & 0xFF));
    platform_spi_write_reg(ICM42688_REG_FIFO_CONFIG3, (uint8_t)((wm_bytes >> 8) & 0x0F));

    /* 6. Увімкнення генерації кадру Packet 3 (Header + Accel + Gyro + Temp + Timestamp) */
    platform_spi_write_reg(ICM42688_REG_FIFO_CONFIG1, 0x07);

    /* 7. Переведення FIFO у режим Stream (циклічне перезаписування) */
    platform_spi_write_reg(ICM42688_REG_FIFO_CONFIG, 0x40);
}

/* Обробник переривання EXTI від піна INT1 (Watermark Threshold) */
void imu_exti_watermark_isr(void) {
    if (g_imu_drv.dma_in_progress) {
        return; /* Захист від повторного входу, якщо попередній трансфер ще триває */
    }

    g_imu_drv.dma_in_progress = true;
    uint8_t *target_buf = g_imu_drv.active_buffer_is_pong ? 
                          g_imu_drv.dma_rx_buf_pong : 
                          g_imu_drv.dma_rx_buf_ping;

    /* Запуск апаратного неблокуючого SPI DMA зчитування */
    platform_spi_start_dma(g_imu_drv.dma_tx_dummy, target_buf, DMA_BURST_BUFFER_SIZE + 1);
}

/* Зворотний виклик завершення передачі по SPI DMA (DMA Transfer Complete ISR) */
void imu_spi_dma_complete_callback(void) {
    g_imu_drv.dma_in_progress = false;
    g_imu_drv.data_ready_for_processing = true;
    g_imu_drv.active_buffer_is_pong = !g_imu_drv.active_buffer_is_pong;
}

/* Парсер потоку байтів: витягує фізичні величини з сирого буфера */
size_t imu_parse_received_batch(imu_packet_t *out_packets, size_t max_packets) {
    if (!g_imu_drv.data_ready_for_processing) {
        return 0;
    }

    g_imu_drv.data_ready_for_processing = false;
    
    /* Читаємо з буфера, який щойно заповнив DMA (протилежний до поточного активного) */
    const uint8_t *raw_stream = g_imu_drv.active_buffer_is_pong ? 
                                g_imu_drv.dma_rx_buf_ping + 1 : 
                                g_imu_drv.dma_rx_buf_pong + 1;

    size_t packet_idx = 0;
    size_t byte_offset = 0;

    while (byte_offset + PACKET_SIZE_BYTES <= DMA_BURST_BUFFER_SIZE && packet_idx < max_packets) {
        uint8_t header = raw_stream[byte_offset];

        /* Перевірка на порожній кадр */
        if (header & FIFO_FRAME_EMPTY_MARKER) {
            break;
        }

        /* Перевірка валідності кадру Packet 3 (Header має містити біти Accel та Gyro) */
        if ((header & (FIFO_FRAME_HEADER_ACCEL_BIT | FIFO_FRAME_HEADER_GYRO_BIT)) == 
            (FIFO_FRAME_HEADER_ACCEL_BIT | FIFO_FRAME_HEADER_GYRO_BIT)) {
            
            int16_t raw_ax = (int16_t)((raw_stream[byte_offset + 1] << 8) | raw_stream[byte_offset + 2]);
            int16_t raw_ay = (int16_t)((raw_stream[byte_offset + 3] << 8) | raw_stream[byte_offset + 4]);
            int16_t raw_az = (int16_t)((raw_stream[byte_offset + 5] << 8) | raw_stream[byte_offset + 6]);

            int16_t raw_gx = (int16_t)((raw_stream[byte_offset + 7] << 8) | raw_stream[byte_offset + 8]);
            int16_t raw_gy = (int16_t)((raw_stream[byte_offset + 9] << 8) | raw_stream[byte_offset + 10]);
            int16_t raw_gz = (int16_t)((raw_stream[byte_offset + 11] << 8) | raw_stream[byte_offset + 12]);

            int8_t raw_temp = (int8_t)raw_stream[byte_offset + 13];
            uint16_t raw_ts = (uint16_t)((raw_stream[byte_offset + 14] << 8) | raw_stream[byte_offset + 15]);

            /* Конвертація в одиниці СІ */
            out_packets[packet_idx].accel[0] = raw_ax * ACCEL_SCALE_FACTOR_16G;
            out_packets[packet_idx].accel[1] = raw_ay * ACCEL_SCALE_FACTOR_16G;
            out_packets[packet_idx].accel[2] = raw_az * ACCEL_SCALE_FACTOR_16G;

            out_packets[packet_idx].gyro[0] = raw_gx * GYRO_SCALE_FACTOR_2000DPS;
            out_packets[packet_idx].gyro[1] = raw_gy * GYRO_SCALE_FACTOR_2000DPS;
            out_packets[packet_idx].gyro[2] = raw_gz * GYRO_SCALE_FACTOR_2000DPS;

            out_packets[packet_idx].temperature = (raw_temp / 2.07f) + 25.0f;
            out_packets[packet_idx].timestamp_us = (uint32_t)raw_ts * 16; /* 16 мкс на такт */

            packet_idx++;
            byte_offset += PACKET_SIZE_BYTES;
        } else {
            /* Втрата синхронізації кадру: зсуваємося на 1 байт для пошуку валідного заголовка */
            byte_offset++;
        }
    }

    return packet_idx;
}
