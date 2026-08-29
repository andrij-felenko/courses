#include "at_urc.h"

#include <string.h>

void at_urc_init(at_urc_table_t *table)
{
    memset(table, 0, sizeof(*table));
}

bool at_urc_register(at_urc_table_t *table, const char *prefix,
                     at_urc_cb_t handler, void *ctx)
{
    if (prefix == NULL || handler == NULL) {
        return false;
    }
    if (table->count >= AT_MAX_URC_HANDLERS) {
        return false;
    }
    const size_t len = strlen(prefix);
    if (len == 0U || len >= AT_MAX_PREFIX_SIZE) {
        return false;
    }

    at_urc_entry_t *slot = &table->entry[table->count];
    memcpy(slot->prefix, prefix, len + 1U);
    slot->handler = handler;
    slot->ctx     = ctx;
    slot->hits    = 0U;
    table->count  = (uint8_t)(table->count + 1U);
    return true;
}

bool at_urc_dispatch(at_urc_table_t *table, const char *line)
{
    at_urc_entry_t *best = NULL;
    size_t best_len = 0U;

    for (uint8_t i = 0U; i < table->count; ++i) {
        at_urc_entry_t *e = &table->entry[i];
        const size_t len = strlen(e->prefix);
        if (len > best_len && strncmp(line, e->prefix, len) == 0) {
            best     = e;
            best_len = len;
        }
    }

    if (best == NULL) {
        return false;
    }

    best->hits++;
    /* Обробник має право покласти команду в чергу: черга захищена критичною
       секцією, а автомат рушія її в цю мить не чіпає — вибірка з черги
       відбувається пізніше, окремою фазою at_engine_poll. */
    best->handler(line, best->ctx);
    return true;
}
