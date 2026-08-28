#include <stdint.h>

/* Регістри одного каналу DMA (адреси умовні, з даташита) */
#define DMA_SRC    (*(volatile uint32_t *)0x3FF1F000)  /* адреса джерела     */
#define DMA_DST    (*(volatile uint32_t *)0x3FF1F004)  /* адреса призначення */
#define DMA_LEN    (*(volatile uint32_t *)0x3FF1F008)  /* кількість байтів   */
#define DMA_CTRL   (*(volatile uint32_t *)0x3FF1F00C)  /* регістр керування  */

#define DMA_DIR_M2P  (1u << 1)   /* напрям: пам'ять → периферія */
#define DMA_WIDTH_32 (2u << 2)   /* ширина слова: 32 біти       */
#define DMA_IE_DONE  (1u << 8)   /* дозволити переривання «готово» */
#define DMA_START    (1u << 0)   /* запуск каналу                */

/* Налаштувати й запустити одну передачу пам'ять → периферія */
void dma_start_tx(const void *src, volatile void *dst, uint32_t nbytes) {
    DMA_SRC  = (uint32_t)src;          /* звідки беремо   */
    DMA_DST  = (uint32_t)dst;          /* куди кладемо    */
    DMA_LEN  = nbytes;                 /* скільки байтів  */
    DMA_CTRL = DMA_DIR_M2P | DMA_WIDTH_32 | DMA_IE_DONE | DMA_START;
    /* керування повернулося негайно — копіює вже DMA, не ядро */
}
