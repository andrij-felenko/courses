#include "trail.h"

#include <math.h>
#include <string.h>

void esc_trail_init(BreadcrumbTrail* t)
{
    memset(t, 0, sizeof *t);
}

uint16_t esc_trail_count(const BreadcrumbTrail* t)
{
    return t->count;
}

float esc_dist2d(const BreadcrumbPoint* a, const BreadcrumbPoint* b)
{
    const float dx = a->x - b->x;
    const float dy = a->y - b->y;
    return sqrtf(dx * dx + dy * dy);
}

static const BreadcrumbPoint* last_point(const BreadcrumbTrail* t)
{
    if (t->count == 0u) return NULL;
    const uint16_t idx = (uint16_t)((t->head + ESC_TRAIL_CAPACITY - 1u) % ESC_TRAIL_CAPACITY);
    return &t->buf[idx];
}

/* Повертає true, якщо точку справді записано */
bool esc_trail_push_if_moved(BreadcrumbTrail* t, const BreadcrumbPoint* p)
{
    const BreadcrumbPoint* last = last_point(t);
    if (last != NULL && esc_dist2d(last, p) < ESC_TRAIL_STEP_M) {
        return false;   /* стоїмо або повземо — сліду не додаємо */
    }
    t->buf[t->head] = *p;
    t->head = (uint16_t)((t->head + 1u) % ESC_TRAIL_CAPACITY);
    if (t->count < ESC_TRAIL_CAPACITY) {
        t->count++;
    }
    return true;
}

/* Знімає найсвіжішу точку — рух назад іде саме в такому порядку */
bool esc_trail_pop_reverse(BreadcrumbTrail* t, BreadcrumbPoint* out)
{
    if (t->count == 0u) return false;
    t->head = (uint16_t)((t->head + ESC_TRAIL_CAPACITY - 1u) % ESC_TRAIL_CAPACITY);
    *out = t->buf[t->head];
    t->count--;
    return true;
}
