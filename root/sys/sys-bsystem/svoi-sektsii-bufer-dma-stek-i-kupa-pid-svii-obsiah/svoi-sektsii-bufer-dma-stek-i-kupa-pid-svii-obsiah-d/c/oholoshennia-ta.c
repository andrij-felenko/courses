#include <stdint.h>
#include <stdbool.h>

#define ETH_RX_BUFFER_SIZE 1536
#define ETH_RX_BUF_COUNT   4

/* Розміщення буферів у виділеній секції .dma_buffer з вирівнюванням на 32 байти */
__attribute__((section(".dma_buffer"), aligned(32)))
static uint8_t eth_rx_buffers[ETH_RX_BUF_COUNT][ETH_RX_BUFFER_SIZE];

/* Дескриптор кільцевого буфера DMA */
typedef struct {
    volatile uint32_t status;
    volatile uint32_t control;
    volatile uint32_t buffer_addr;
    volatile uint32_t next_desc;
} DmaDescriptor_t;

__attribute__((section(".dma_buffer"), aligned(32)))
static DmaDescriptor_t dma_rx_ring[ETH_RX_BUF_COUNT];

/* Змінна, що зберігає код перезавантаження між рестартами ядра */
__attribute__((section(".noinit")))
static uint32_t reset_reason_magic;

/* Функція, що виконується з надшвидкої пам'яті ITCM */
__attribute__((section(".ram_code"), noinline))
float Fast_Inverse_Sqrt(float x) {
    float xhalf = 0.5f * x;
    union { float f; uint32_t i; } conv = { .f = x };
    conv.i = 0x5f3759df - (conv.i >> 1);
    conv.f *= (1.5f - (xhalf * conv.f * conv.f));
    return conv.f;
}
