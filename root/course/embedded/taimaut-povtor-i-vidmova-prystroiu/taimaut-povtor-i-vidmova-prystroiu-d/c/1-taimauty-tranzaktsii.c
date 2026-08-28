#include <stdint.h>
#include <stdbool.h>

/* Безпечне аварійне скасування завислої транзакції DMA */
bool dma_abort_transfer(DMA_Stream_TypeDef *dma_stream, timeout_dwt_t *guard) {
    /* Примусово скидаємо біт увімкнення потоку DMA */
    dma_stream->CR &= ~DMA_SxCR_EN;

    /* Чекаємо апаратного підтвердження зупинки конвеєра */
    while (dma_stream->CR & DMA_SxCR_EN) {
        if (timeout_dwt_expired(guard)) {
            /* Фатальний збій шинної матриці контролера DMA */
            return false;
        }
    }

    /* Очищаємо прапорці переривань потоку */
    return true;
}
