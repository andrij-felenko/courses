#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define IMU_PACKET_SIZE       14   /* 6 байтів Accel + 6 байтів Gyro + 2 байти Temp */
#define RING_BUFFER_CAPACITY  64

/* Структура сирого пакета з апаратною міткою часу */
typedef struct {
    uint32_t timestamp_us;         /* Значення захопленого лічильника TIM2 */
    int16_t accel_raw[3];          /* Осі X, Y, Z */
    int16_t gyro_raw[3];           /* Осі X, Y, Z */
    int16_t temp_raw;
    uint8_t sensor_id;
    uint8_t status_flags;
} ImuSampleFrame;

/* Кільцевий буфер синхронізованих кадрів */
typedef struct {
    ImuSampleFrame frames[RING_BUFFER_CAPACITY];
    volatile uint32_t head;
    volatile uint32_t tail;
} ImuRingBuffer;

static ImuRingBuffer g_imu_ring;
static uint8_t g_spi1_rx_dma_buf[IMU_PACKET_SIZE];
static uint8_t g_spi2_rx_dma_buf[IMU_PACKET_SIZE];
static uint8_t g_spi_tx_dummy[IMU_PACKET_SIZE] = {0x80 | 0x1F, 0}; /* Читання з регістру FIFO */

/* Ініціалізація кільцевого буфера */
void imu_ring_buffer_init(void) {
    g_imu_ring.head = 0;
    g_imu_ring.tail = 0;
}

/* Перевірка наявності нових зразків */
bool imu_ring_buffer_pop(ImuSampleFrame *out_frame) {
    if (g_imu_ring.head == g_imu_ring.tail) {
        return false; /* Буфер порожній */
    }
    *out_frame = g_imu_ring.frames[g_imu_ring.tail];
    g_imu_ring.tail = (g_imu_ring.tail + 1) % RING_BUFFER_CAPACITY;
    return true;
}

/* Обробник переривання EXTI для лінії DRDY IMU 1 */
void EXTI0_IRQHandler(void) {
    /* 1. Зчитуємо апаратно захоплену мітку часу з регістру захоплення TIM2 */
    uint32_t captured_time_us = TIM2->CCR1;

    /* 2. Опускаємо лінію Chip Select (CS) для SPI1 */
    GPIOA->BSRR = (1U << (4 + 16)); /* PA4 = LOW (CS active) */

    /* 3. Конфігуруємо та запускаємо передачу DMA для читання пакета */
    DMA1_Stream0->NDTR = IMU_PACKET_SIZE;
    DMA1_Stream0->M0AR = (uint32_t)g_spi1_rx_dma_buf;
    DMA1_Stream0->CR |= DMA_SxCR_EN;

    DMA1_Stream3->NDTR = IMU_PACKET_SIZE;
    DMA1_Stream3->M0AR = (uint32_t)g_spi_tx_dummy;
    DMA1_Stream3->CR |= DMA_SxCR_EN;

    /* Скидання прапорця переривання EXTI */
    EXTI->PR = EXTI_PR_PR0;
}

/* Обробник завершення DMA передачі SPI1 */
void DMA1_Stream0_IRQHandler(void) {
    if (DMA1->LISR & DMA_LISR_TCIF0) {
        DMA1->LIFCR = DMA_LIFCR_CTCIF0;

        /* Піднімаємо CS (PA4 = HIGH) */
        GPIOA->BSRR = (1U << 4);

        /* Розбір отриманого кадру та збереження в кільцевий буфер */
        uint32_t next_head = (g_imu_ring.head + 1) % RING_BUFFER_CAPACITY;
        if (next_head != g_imu_ring.tail) {
            ImuSampleFrame *frame = &g_imu_ring.frames[g_imu_ring.head];
            frame->timestamp_us = TIM2->CCR1;
            frame->sensor_id = 1;

            /* Розпакування 16-бітних слів Big-Endian */
            frame->accel_raw[0] = (int16_t)((g_spi1_rx_dma_buf[1] << 8) | g_spi1_rx_dma_buf[2]);
            frame->accel_raw[1] = (int16_t)((g_spi1_rx_dma_buf[3] << 8) | g_spi1_rx_dma_buf[4]);
            frame->accel_raw[2] = (int16_t)((g_spi1_rx_dma_buf[5] << 8) | g_spi1_rx_dma_buf[6]);

            frame->temp_raw = (int16_t)((g_spi1_rx_dma_buf[7] << 8) | g_spi1_rx_dma_buf[8]);

            frame->gyro_raw[0] = (int16_t)((g_spi1_rx_dma_buf[9] << 8) | g_spi1_rx_dma_buf[10]);
            frame->gyro_raw[1] = (int16_t)((g_spi1_rx_dma_buf[11] << 8) | g_spi1_rx_dma_buf[12]);
            frame->gyro_raw[2] = (int16_t)((g_spi1_rx_dma_buf[13] << 8) | g_spi1_rx_dma_buf[14]);

            g_imu_ring.head = next_head;
        }
    }
}
