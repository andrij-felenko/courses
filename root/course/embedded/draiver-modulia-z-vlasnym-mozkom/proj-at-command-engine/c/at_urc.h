#ifndef AT_URC_H
#define AT_URC_H

#include <stdbool.h>
#include <stdint.h>

#include "at_config.h"

/* Обробник спонтанного сповіщення. Викликається з контексту головного циклу
   (з at_engine_poll), а НЕ з переривання UART: класти команду в чергу зсередини
   ISR — це пошкоджені індекси FIFO або взаємне блокування. */
typedef void (*at_urc_cb_t)(const char *line, void *ctx);

typedef struct {
    char        prefix[AT_MAX_PREFIX_SIZE];
    at_urc_cb_t handler;
    void       *ctx;
    uint16_t    hits;
} at_urc_entry_t;

typedef struct {
    at_urc_entry_t entry[AT_MAX_URC_HANDLERS];
    uint8_t        count;
} at_urc_table_t;

void at_urc_init(at_urc_table_t *table);

bool at_urc_register(at_urc_table_t *table, const char *prefix,
                     at_urc_cb_t handler, void *ctx);

/* true, якщо рядок розпізнано як URC і віддано обробнику. Пошук за найдовшим
   збігом: "+QIURC: \"closed\"" мусить виграти в загального "+QIURC:". */
bool at_urc_dispatch(at_urc_table_t *table, const char *line);

#endif /* AT_URC_H */
