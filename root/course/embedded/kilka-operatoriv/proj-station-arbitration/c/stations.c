#include "stations.h"

#include <string.h>

void station_table_init(station_table_t *t)
{
    memset(t, 0, sizeof(*t));
}

static station_t *find_mutable(station_table_t *t, uint8_t id)
{
    for (unsigned i = 0; i < ARB_MAX_STATIONS; ++i) {
        if (t->slot[i].used && t->slot[i].id == id) {
            return &t->slot[i];
        }
    }
    return NULL;
}

station_t *station_touch(station_table_t *t, uint8_t id, uint8_t roles, uint32_t now_ms)
{
    station_t *s = find_mutable(t, id);
    if (s != NULL) {
        /* Ролі беремо з кожного heartbeat: станція могла перезапуститися
         * з іншим набором повноважень, і борт мусить це побачити. */
        s->roles = roles;
        s->last_seen_ms = now_ms;
        return s;
    }
    for (unsigned i = 0; i < ARB_MAX_STATIONS; ++i) {
        if (!t->slot[i].used) {
            t->slot[i].used = true;
            t->slot[i].id = id;
            t->slot[i].roles = roles;
            t->slot[i].last_seen_ms = now_ms;
            return &t->slot[i];
        }
    }
    return NULL; /* вісім слотів скінчилися — дев'ятий пульт борт не бачить */
}

const station_t *station_find(const station_table_t *t, uint8_t id)
{
    for (unsigned i = 0; i < ARB_MAX_STATIONS; ++i) {
        if (t->slot[i].used && t->slot[i].id == id) {
            return &t->slot[i];
        }
    }
    return NULL;
}

bool station_is_alive(const station_table_t *t, uint8_t id, uint32_t now_ms, uint32_t lease_ms)
{
    const station_t *s = station_find(t, id);
    if (s == NULL) {
        return false;
    }
    return (uint32_t)(now_ms - s->last_seen_ms) <= lease_ms;
}

bool station_has_role(const station_table_t *t, uint8_t id, uint8_t role,
                      uint32_t now_ms, uint32_t lease_ms)
{
    const station_t *s = station_find(t, id);
    if (s == NULL || (s->roles & role) == 0u) {
        return false;
    }
    return (uint32_t)(now_ms - s->last_seen_ms) <= lease_ms;
}

void station_expire(station_table_t *t, uint32_t now_ms)
{
    for (unsigned i = 0; i < ARB_MAX_STATIONS; ++i) {
        if (!t->slot[i].used) {
            continue;
        }
        if ((uint32_t)(now_ms - t->slot[i].last_seen_ms) > ARB_STATION_TTL_MS) {
            memset(&t->slot[i], 0, sizeof(t->slot[i]));
        }
    }
}
