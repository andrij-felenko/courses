#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FIFO_TAG_EMPTY         0x00
#define FIFO_TAG_GYRO          0x01
#define FIFO_TAG_ACCEL         0x02
#define FIFO_TAG_TIMESTAMP     0x04
#define FIFO_SLOT_SIZE         7
#define FIFO_WATERMARK_SLOTS   64
#define FIFO_DMA_BUFFER_SIZE   (FIFO_WATERMARK_SLOTS * FIFO_SLOT_SIZE + 1) // +1 байт адреси регістра

#define RING_BUFFER_CAPACITY   256

// Структура одного фізичного виміру сенсора
typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
    uint32_t timestamp_us;
} ImuSample;

// Потокобезпечний кільцевий буфер для взаємодії переривання з фоновою задачею
typedef struct {
    ImuSample buffer[RING_BUFFER_CAPACITY];
    volatile uint16_t head;
    volatile uint16_t tail;
    volatile uint32_t dropped_samples;
} ImuRingBuffer;

static ImuRingBuffer g_accel_ring;
static ImuRingBuffer g_gyro_ring;

// Буфери DMA повинні мати жорстке 32-байтне вирівнювання для коректної інвалідації D-Cache
__attribute__((aligned(32))) static uint8_t g_spi_tx_buf[FIFO_DMA_BUFFER_SIZE];
__attribute__((aligned(32))) static uint8_t g_spi_rx_buf[FIFO_DMA_BUFFER_SIZE];
static volatile bool g_dma_in_progress = false;

// Апаратні виклики низького рівня (BSP)
extern void bsp_spi_select(void);
extern void bsp_spi_deselect(void);
extern void bsp_spi_transfer_dma(const uint8_t *tx, uint8_t *rx, uint16_t len);
extern void bsp_sensor_fifo_reset(void);
extern uint32_t bsp_get_system_micros(void);
extern void bsp_dcache_invalidate(void *addr, uint32_t size);

void imu_ring_init(ImuRingBuffer *rb) {
    rb->head = 0;
    rb->tail = 0;
    rb->dropped_samples = 0;
}

void imu_ring_push(ImuRingBuffer *rb, const ImuSample *sample) {
    uint16_t next_head = (rb->head + 1) % RING_BUFFER_CAPACITY;
    if (next_head != rb->tail) {
        rb->buffer[rb->head] = *sample;
        rb->head = next_head;
    } else {
        rb->dropped_samples++; // Переповнення кільцевого буфера застосунку
    }
}

bool imu_ring_pop(ImuRingBuffer *rb, ImuSample *out_sample) {
    if (rb->head == rb->tail) {
        return false; // Буфер порожній
    }
    *out_sample = rb->buffer[rb->tail];
    rb->tail = (rb->tail + 1) % RING_BUFFER_CAPACITY;
    return true;
}

// 1. Апаратний обробник зовнішнього переривання (EXTI) по лінії Watermark
void EXTI_Sensor_Watermark_ISR(void) {
    if (!g_dma_in_progress) {
        g_dma_in_progress = true;
        
        // Формування команди читання з автоінкрементом для вікна FIFO_DATA_OUT (0x78)
        // Для шини SPI біт 7 встановлюється в 1 (Read: 0x80 | 0x78 = 0xF8)
        g_spi_tx_buf[0] = 0x78 | 0x80;
        memset(&g_spi_tx_buf[1], 0x00, FIFO_DMA_BUFFER_SIZE - 1);
        
        bsp_spi_select();
        bsp_spi_transfer_dma(g_spi_tx_buf, g_spi_rx_buf, FIFO_DMA_BUFFER_SIZE);
    }
}

// 2. Колбек завершення пересилання DMA (викликається контролером DMA по перериванню)
void DMA_SPI_RxComplete_Callback(void) {
    bsp_spi_deselect();
    g_dma_in_progress = false;

    // Інвалідація кешу даних процесора перед читанням пам'яті, заповненої DMA
    bsp_dcache_invalidate(g_spi_rx_buf, FIFO_DMA_BUFFER_SIZE);

    // Перший байт RX є сміттям (фаза адреси), корисний потік починається з індексу 1
    const uint8_t *raw_stream = &g_spi_rx_buf[1];
    uint16_t total_bytes = FIFO_DMA_BUFFER_SIZE - 1;
    uint32_t now = bsp_get_system_micros();

    for (uint16_t i = 0; i + FIFO_SLOT_SIZE <= total_bytes; i += FIFO_SLOT_SIZE) {
        const uint8_t *slot = &raw_stream[i];
        uint8_t tag = (slot[0] >> 3) & 0x1F; // Виділення 5-бітного коду тегу

        ImuSample sample;
        // Збирання 16-бітних знакових слів із пари байтів (Little-Endian)
        sample.x = (int16_t)((uint16_t)slot[1] | ((uint16_t)slot[2] << 8));
        sample.y = (int16_t)((uint16_t)slot[3] | ((uint16_t)slot[4] << 8));
        sample.z = (int16_t)((uint16_t)slot[5] | ((uint16_t)slot[6] << 8));
        sample.timestamp_us = now;

        switch (tag) {
            case FIFO_TAG_ACCEL:
                imu_ring_push(&g_accel_ring, &sample);
                break;
            case FIFO_TAG_GYRO:
                imu_ring_push(&g_gyro_ring, &sample);
                break;
            case FIFO_TAG_EMPTY:
                // Досягнуто кінця валідних даних: буфер вичитано повністю
                return;
            default:
                // Невідомий або пошкоджений тег: ознака фазового збою потоку
                bsp_sensor_fifo_reset();
                return;
        }
    }
}
