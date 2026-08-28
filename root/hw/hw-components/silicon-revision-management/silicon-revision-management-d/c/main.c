/* silicon_quirk_dispatch.h - Архітектура диспетчеризації мовою C */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define QUIRK_I2C_BUSY_LOCK   (1U << 0)
#define QUIRK_UART_DMA_CORRUPT (1U << 1)
#define QUIRK_ADC_REF_DRIFT    (1U << 2)

typedef struct {
    uint16_t rev_id;
    uint32_t active_quirks;
} silicon_entry_t;

static const silicon_entry_t QUIRK_REGISTRY[] = {
    { 0x1000, QUIRK_I2C_BUSY_LOCK | QUIRK_UART_DMA_CORRUPT }, /* Rev A0 */
    { 0x1001, QUIRK_UART_DMA_CORRUPT },                       /* Rev A1 */
    { 0x2000, 0 }                                             /* Rev B0 (Fixed) */
};

static uint32_t g_active_quirks = 0;

void silicon_init_quirks(uint16_t hw_rev_id) {
    g_active_quirks = 0;
    for (size_t i = 0; i < sizeof(QUIRK_REGISTRY)/sizeof(QUIRK_REGISTRY[0]); ++i) {
        if (QUIRK_REGISTRY[i].rev_id == hw_rev_id) {
            g_active_quirks = QUIRK_REGISTRY[i].active_quirks;
            break;
        }
    }
}

static inline bool silicon_has_quirk(uint32_t quirk_flag) {
    return (g_active_quirks & quirk_flag) != 0;
}

/* Приклад використання в драйвері UART */
void uart_transmit_complete_handler(volatile uint32_t *uart_sr) {
    if (silicon_has_quirk(QUIRK_UART_DMA_CORRUPT)) {
        /* Обхідний шлях: обов'язкове очікування біта TC перед скиданням DMA */
        while (!(*uart_sr & (1U << 6))) { /* wait TC */ }
    }
}
