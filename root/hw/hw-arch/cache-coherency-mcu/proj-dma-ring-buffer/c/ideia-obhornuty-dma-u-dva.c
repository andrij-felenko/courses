#include <stdint.h>
#include "stm32h7xx.h"   // дає SCB_* та регістри периферії/DMA

// Буфер під DMA-приймання: власний рядок(-и) кеша, нікого поруч.
// aligned(32) — старт на межі 32; розмір кратний 32 — рівно ціле число рядків.
#define RX_LEN   64u   // 64 = 2 × 32
static uint8_t rx_buf[RX_LEN] __attribute__((aligned(32)));

// Викликається, коли DMA підняв «передавання завершено».
void on_dma_rx_complete(void)
{
    // 1) Викинути стару копію рядків буфера з кеша.
    SCB_InvalidateDCache_by_Addr((uint32_t *)rx_buf, RX_LEN);
    // 2) ТЕПЕР читання йде в SRAM за свіжим — це справді те, що приніс DMA.
    process_packet(rx_buf, RX_LEN);
}
