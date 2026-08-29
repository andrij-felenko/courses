#ifndef AT_RING_H
#define AT_RING_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "at_config.h"

/* Кільцевий буфер прийому UART DMA у циклічному режимі.

   Покажчик запису (head) не зберігається взагалі — він живе в апаратному
   регістрі DMA_CNDTR і обчислюється щоразу заново. Покажчик читання (tail)
   рухає тільки парсер. Кожен покажчик має рівно одного власника, тому
   читання не вимагає вимкнення переривань. */
typedef struct {
    uint8_t  data[AT_RX_BUFFER_SIZE];
    uint16_t tail;
} at_ring_t;

typedef enum {
    AT_LINE_NONE = 0,   /* '\n' ще не прийшов — tail лишився на місці */
    AT_LINE_OK,         /* рядок виділено */
    AT_LINE_EMPTY,      /* порожній рядок (роздільник у відповіді модуля) */
    AT_LINE_OVERFLOW    /* перевищено AT_MAX_LINE_SIZE, сміття викинуто */
} at_line_status_t;

void at_ring_init(at_ring_t *ring);

/* Куди націлювати DMA. */
static inline uint8_t *at_ring_dma_target(at_ring_t *ring) { return ring->data; }
static inline uint16_t at_ring_capacity(void) { return (uint16_t)AT_RX_BUFFER_SIZE; }

/* DMA_CNDTR рахує НЕДОпередані байти, тож покажчик запису — це різниця. */
static inline uint16_t at_ring_head(uint16_t dma_cndtr)
{
    return (uint16_t)((AT_RX_BUFFER_SIZE - dma_cndtr) & AT_RX_MASK);
}

uint16_t at_ring_available(const at_ring_t *ring, uint16_t head);

/* Витягує один рядок до '\n'. Поки термінатора немає — tail НЕ рухається:
   саме це рятує URC, розірваний модулем на два кадри. */
at_line_status_t at_ring_read_line(at_ring_t *ring, uint16_t head,
                                   char *out, size_t out_size);

/* Шукає одиничний символ (запрошення '>'), який не завершується '\n'.
   Знайшовши, з'їдає все до нього включно. */
bool at_ring_take_upto(at_ring_t *ring, uint16_t head, char ch);

/* Викидає все прийняте. Потрібно після таймауту: у буфері лишається хвіст
   напівприйнятої відповіді, який інакше зсунув би розбір наступної команди. */
void at_ring_flush(at_ring_t *ring, uint16_t head);

#endif /* AT_RING_H */
