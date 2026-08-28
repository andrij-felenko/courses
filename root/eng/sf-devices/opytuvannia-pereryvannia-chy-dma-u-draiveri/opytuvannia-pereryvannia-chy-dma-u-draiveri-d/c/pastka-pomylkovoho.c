#include <stdint.h>
#include <stddef.h>
#include <string.h>

extern void SCB_CleanDCache_by_Addr(uint32_t *addr, int32_t dsize);
extern void SCB_InvalidateDCache_by_Addr(uint32_t *addr, int32_t dsize);

#define CACHE_LINE_SIZE 32
#define ROUND_UP_32(x) (((x) + (CACHE_LINE_SIZE - 1)) & ~(CACHE_LINE_SIZE - 1))

__attribute__((aligned(32))) static uint8_t g_tx_payload[ROUND_UP_32(128)];
__attribute__((aligned(32))) static uint8_t g_rx_payload[ROUND_UP_32(128)];

void Driver_PrepareTxDma(const uint8_t *src_data, size_t length) {
    if (length > sizeof(g_tx_payload)) return;

    memcpy(g_tx_payload, src_data, length);

    // 1. Виштовхуємо дані з кешу в SRAM перед читанням DMA
    SCB_CleanDCache_by_Addr((uint32_t *)g_tx_payload, (int32_t)sizeof(g_tx_payload));

    // 2. Апаратний бар'єр пам'яті
    __asm volatile ("dsb" ::: "memory");
}

void Driver_ProcessRxDma(uint8_t *dst_data, size_t length) {
    // 1. Скидаємо старі копії з кешу ПЕРЕД читанням процесором
    SCB_InvalidateDCache_by_Addr((uint32_t *)g_rx_payload, (int32_t)sizeof(g_rx_payload));

    __asm volatile ("dsb" ::: "memory");

    // 2. Тепер читання гарантовано повертає свіжі дані з фізичної SRAM
    memcpy(dst_data, g_rx_payload, length);
}
