#include "sf_ackset.h"

#include <string.h>

void sf_ackset_reset(sf_ackset_t *s)
{
    memset(s, 0, sizeof(*s));
}

static void remove_at(sf_ackset_t *s, uint8_t idx)
{
    for (uint8_t i = idx; i + 1u < s->count; i++) {
        s->r[i] = s->r[i + 1u];
    }
    s->count--;
}

static void insert_at(sf_ackset_t *s, uint8_t idx, uint32_t lo, uint32_t hi)
{
    for (uint8_t i = s->count; i > idx; i--) {
        s->r[i] = s->r[i - 1u];
    }
    s->r[idx].lo = lo;
    s->r[idx].hi = hi;
    s->count++;
}

/* Викидаємо найкоротший діапазон: він коштує найменше повторів. */
static void evict_cheapest(sf_ackset_t *s)
{
    uint8_t victim = 0;
    uint32_t best = 0xFFFFFFFFu;

    for (uint8_t i = 0; i < s->count; i++) {
        const uint32_t width = s->r[i].hi - s->r[i].lo + 1u;
        if (width < best) {
            best = width;
            victim = i;
        }
    }
    remove_at(s, victim);
    s->dropped++;
}

bool sf_ackset_add_range(sf_ackset_t *s, uint32_t lo, uint32_t hi)
{
    uint8_t i;

    if (lo > hi) {
        return true;
    }

    /* Поглинаємо все, що дотикається або перекривається. Дотик рахуємо
     * за сусідством номерів: [4..7] і [8..9] — це один суцільний шматок,
     * і зливати їх чесно. */
    i = 0;
    while (i < s->count) {
        const bool touches = (s->r[i].lo <= hi + 1u) && (lo <= s->r[i].hi + 1u);

        if (touches) {
            if (s->r[i].lo < lo) {
                lo = s->r[i].lo;
            }
            if (s->r[i].hi > hi) {
                hi = s->r[i].hi;
            }
            remove_at(s, i);
            continue; /* після зсуву на цьому індексі вже інший діапазон */
        }
        i++;
    }

    bool full = false;
    if (s->count == SF_ACK_RANGES) {
        evict_cheapest(s);
        full = true;
    }

    /* Тримаємо таблицю впорядкованою — так contains і prune лишаються
     * лінійними без сортування. */
    for (i = 0; i < s->count; i++) {
        if (lo < s->r[i].lo) {
            break;
        }
    }
    insert_at(s, i, lo, hi);
    return !full;
}

bool sf_ackset_contains(const sf_ackset_t *s, uint32_t seq)
{
    for (uint8_t i = 0; i < s->count; i++) {
        if (seq >= s->r[i].lo && seq <= s->r[i].hi) {
            return true;
        }
        if (seq < s->r[i].lo) {
            break; /* таблиця впорядкована — далі тільки більші */
        }
    }
    return false;
}

void sf_ackset_prune_below(sf_ackset_t *s, uint32_t seq)
{
    uint8_t i = 0;

    while (i < s->count) {
        if (s->r[i].hi < seq) {
            remove_at(s, i);
            continue;
        }
        if (s->r[i].lo < seq) {
            s->r[i].lo = seq;
        }
        i++;
    }
}
