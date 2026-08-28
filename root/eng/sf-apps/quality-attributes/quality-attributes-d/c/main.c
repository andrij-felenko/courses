#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t value;        // збережена відповідь
    uint32_t stored_at_ms; // коли поклали в кеш
    bool     valid;        // чи є що віддавати
} Cache;

// max_age_ms — контракт свіжості: наскільки застарілі дані ми ще
// згодні віддавати. Це ЧИСЛО зі сценарію атрибута, а не випадкова стала.
bool cache_get(const Cache *c, uint32_t now_ms,
               uint32_t max_age_ms, uint32_t *out) {
    if (!c->valid)
        return false;                       // кеш порожній — доведеться рахувати
    if (now_ms - c->stored_at_ms > max_age_ms)
        return false;                       // застаріло понад дозволене — теж рахувати
    *out = c->value;                        // свіже — швидкий шлях
    return true;
}
