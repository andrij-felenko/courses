#ifndef WS2812B_DMA_H
#define WS2812B_DMA_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file ws2812b_dma.h
 * @brief Оголошення апаратного абстракційного шару (HAL) для периферифійного контролера DMA та TIM PWM.
 *
 * Описує кільцевий/подвійний буфер DMA, макроси тривалостей паузи RESET (> 50 мкс)
 * та прототипи інтерфейсу зв'язку з апаратними перериваннями Half Transfer (HT) і Transfer Complete (TC).
 */

/**
 * @brief Розмір одного блоку передачі в бітах на 1 піксель (24 біти = 8G + 8R + 8B).
 */
#define WS2812B_BITS_PER_LED       24U

/**
 * @brief Кількість елементів шини DMA в одній половині подвійного буфера (ping-pong buffer).
 * Одна половина містить 24 значення скважності PWM (двохбайтові або чотирьохбайтові відліки для 1 пікселя).
 */
#define WS2812B_DMA_HALF_BUFFER_SIZE  WS2812B_BITS_PER_LED

/**
 * @brief Загальний розмір подвійного буфера DMA в елементах (2 половини * 24 біти = 48 відліків PWM).
 */
#define WS2812B_DMA_BUFFER_SIZE       (WS2812B_DMA_HALF_BUFFER_SIZE * 2U)

/**
 * @brief Мінімальна кількість бітових інтервалів "0" для формування тривалості RESET pulse > 50 мкс.
 * При періоді біта 1.25 мкс, 40 послідовних бітів 0 = 50 мкс. Для гарантованого фіксування 
 * новими чіпами WS2812B використовуємо 64 біти (80 мкс).
 */
#define WS2812B_RESET_BITS_COUNT      64U

/**
 * @brief Тип покажчика на зворотний виклик (callback) при досягненні подій DMA.
 */
struct ws2812b;
typedef void (*ws2812b_dma_callback_t)(struct ws2812b *ws, uint8_t half_idx);

/**
 * @brief Апаратний контекст модуля DMA та таймера.
 */
typedef struct {
    uint16_t dma_buffer[WS2812B_DMA_BUFFER_SIZE]; /**< Кільцевий подвійний буфер DMA значення скважності PWM */
    volatile uint32_t *tim_ccr_reg;               /**< Вказівник на апаратний регістр CCR таймера */
    volatile bool is_active;                       /**< Прапорець активності фонового DMA обміну */
    ws2812b_dma_callback_t half_cplt_cb;          /**< Зворотний виклик Half Transfer (HT ISR) */
    ws2812b_dma_callback_t cplt_cb;               /**< Зворотний виклик Transfer Complete (TC ISR) */
} ws2812b_dma_t;

/* --- Прототипи функцій низкорівневого DMA шару --- */

/**
 * @brief Ініціалізація апаратного контексту DMA та прив'язка регістру таймера.
 *
 * @param dma Вказівник на структури апаратного шару DMA.
 * @param tim_ccr_reg Вказівник на регістр capture/compare (CCR) PWM таймера.
 * @param half_cb Callback для переривання половини передачі (HT).
 * @param cplt_cb Callback для переривання повного завершення (TC).
 * @return true у разі успішної конфігурації.
 */
bool ws2812b_dma_init(ws2812b_dma_t *dma, volatile uint32_t *tim_ccr_reg,
                      ws2812b_dma_callback_t half_cb, ws2812b_dma_callback_t cplt_cb);

/**
 * @brief Запуск циклічної (Circular Mode) передачі DMA даних у регістр TIM CCR.
 *
 * @param dma Вказівник на апаратний контекст.
 * @return true при успішному старті.
 */
bool ws2812b_dma_start(ws2812b_dma_t *dma);

/**
 * @brief Зупинка циклічної передачі DMA та зняття прапорця активності.
 */
void ws2812b_dma_stop(ws2812b_dma_t *dma);

/**
 * @brief Обробник переривання половини передачі (Half Transfer, HT ISR).
 * Викликається безпосередньо з векторного переривання DMA (наприклад, DMA1_Channel1_IRQHandler).
 *
 * @param ws Вказівник на головну структуру C-драйвера WS2812B.
 */
void ws2812b_dma_ht_isr(struct ws2812b *ws);

/**
 * @brief Обробник переривання повного завершення буфера (Transfer Complete, TC ISR).
 * Викликається з векторного переривання DMA при досягненні кінця масиву dma_buffer.
 *
 * @param ws Вказівник на головну структуру C-драйвера WS2812B.
 */
void ws2812b_dma_tc_isr(struct ws2812b *ws);

#endif /* WS2812B_DMA_H */
