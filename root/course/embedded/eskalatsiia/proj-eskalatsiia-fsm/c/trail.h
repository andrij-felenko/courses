#ifndef ESC_TRAIL_H
#define ESC_TRAIL_H

#include <stdbool.h>
#include <stdint.h>

#define ESC_TRAIL_CAPACITY      64u
/* Пишемо точку лише після реального зсуву: зависання на місці інакше
   витіснить із кільця всю траєкторію підльоту однаковими координатами */
#define ESC_TRAIL_STEP_M        1.5f
#define ESC_ACCEPT_RADIUS_M     0.8f
/* Під час відкату одометрія дрейфує — радіус приймання точки подвоюємо */
#define ESC_BACKTRACK_RADIUS_M  (2.0f * ESC_ACCEPT_RADIUS_M)

typedef struct {
    float    x, y, z;
    float    yaw;
    uint32_t timestamp_ms;
    int8_t   rssi_dbm;      /* рівень радіосигналу в цій точці */
} BreadcrumbPoint;

/* Кільцевий буфер історії руху (breadcrumb trail) */
typedef struct {
    BreadcrumbPoint buf[ESC_TRAIL_CAPACITY];
    uint16_t head;
    uint16_t count;
} BreadcrumbTrail;

void     esc_trail_init(BreadcrumbTrail* t);
bool     esc_trail_push_if_moved(BreadcrumbTrail* t, const BreadcrumbPoint* p);
bool     esc_trail_pop_reverse(BreadcrumbTrail* t, BreadcrumbPoint* out);
uint16_t esc_trail_count(const BreadcrumbTrail* t);
float    esc_dist2d(const BreadcrumbPoint* a, const BreadcrumbPoint* b);

#endif /* ESC_TRAIL_H */
