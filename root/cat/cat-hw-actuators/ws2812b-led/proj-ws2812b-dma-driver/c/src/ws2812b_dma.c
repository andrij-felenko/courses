#include "ws2812b_dma.h"
#include "ws2812b.h"
#include <string.h>

/**
 * @file ws2812b_dma.c
 * @brief Реалізація низькорівневої передачі даних DMA для WS2812B.
 *
 * Реалізує конфігурацію кільцевого буфера DMA у режим Circular Mode, підключення
 * до апаратного регістра таймера TIM PWM та векторне розлучення обробників 
 * переривань половини передачі (Half Transfer, HT) і повного завершення (Transfer Complete, TC).
 */

bool ws2812b_dma_init(ws2812b_dma_t *dma, volatile uint32_t *tim_ccr_reg,
                      ws2812b_dma_callback_t half_cb, ws2812b_dma_callback_t cplt_cb) {
    if (!dma || !tim_ccr_reg || !half_cb || !cplt_cb) {
        return false;
    }

    dma->tim_ccr_reg = tim_ccr_reg;
    dma->half_cplt_cb = half_cb;
    dma->cplt_cb = cplt_cb;
    dma->is_active = false;

    /* Обнулення подвійного буфера DMA при ініціалізації */
    memset((void *)dma->dma_buffer, 0, sizeof(dma->dma_buffer));

    return true;
}

bool ws2812b_dma_start(ws2812b_dma_t *dma) {
    if (!dma || !dma->tim_ccr_reg) {
        return false;
    }

    /*
     * В реальному мікроконтролері (наприклад STM32 / SAM / nRF):
     * 1. Вмикається таймер PWM (TIMx->CR1 |= TIM_CR1_CEN).
     * 2. Вмикається запит DMA таймера (TIMx->DIER |= TIM_DIER_CC1DE).
     * 3. Запускається канал DMA у режиме CIRCULAR з розміром буфера WS2812B_DMA_BUFFER_SIZE.
     * 4. Умикаються переривання DMA (HTIE та TCIE).
     */
    dma->is_active = true;
    return true;
}

void ws2812b_dma_stop(ws2812b_dma_t *dma) {
    if (!dma) {
        return;
    }

    /*
     * У реальному залізі:
     * 1. Вимикається канал DMA (DMA_Channel->CCR &= ~DMA_CCR_EN).
     * 2. Регістр таймера CCR скидається в 0 (лінія світлодіодів у низькому рівні LOW).
     */
    dma->is_active = false;
    if (dma->tim_ccr_reg) {
        *(dma->tim_ccr_reg) = WS2812B_DUTY_RESET;
    }
}

void ws2812b_dma_ht_isr(struct ws2812b *ws) {
    if (!ws) {
        return;
    }

    /*
     * Подія Half Transfer (HT): DMA передав першу половину dma_buffer (індекси 0 .. 23).
     * Доки DMA передає другу половину (індекси 24 .. 47), процесор заповнює першу половину (half_idx = 0).
     */
    if (ws->dma_hw.half_cplt_cb) {
        ws->dma_hw.half_cplt_cb(ws, 0);
    }
}

void ws2812b_dma_tc_isr(struct ws2812b *ws) {
    if (!ws) {
        return;
    }

    /*
     * Подія Transfer Complete (TC): DMA передав другу половину dma_buffer (індекси 24 .. 47).
     * Доки DMA знову циклічно (Circular Mode) передає першу половину, процесор заповнює другу (half_idx = 1).
     */
    if (ws->dma_hw.cplt_cb) {
        ws->dma_hw.cplt_cb(ws, 1);
    }
}
