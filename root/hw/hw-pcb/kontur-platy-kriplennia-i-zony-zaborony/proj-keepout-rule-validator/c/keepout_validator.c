/* keepout_validator.c — Повна реалізація валідатора зон заборони на C99 */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAX_VERTICES 32
#define MAX_VIOLATIONS 64
#define MAX_KEEPOUTS 32

#define KEEPOUT_COMPONENT     (1U << 0)  /* 0x01: Заборона компонентів */
#define KEEPOUT_ROUTE         (1U << 1)  /* 0x02: Заборона доріжок     */
#define KEEPOUT_COPPER        (1U << 2)  /* 0x04: Заборона міді        */
#define KEEPOUT_VIA           (1U << 3)  /* 0x08: Заборона перехідних  */
#define KEEPOUT_SMT_RAIL      (1U << 4)  /* 0x10: Поле конвеєра SMT    */

typedef struct {
    double x;
    double y;
} Vec2;

Vec2 vec2_add(Vec2 a, Vec2 b) { return (Vec2){a.x + b.x, a.y + b.y}; }
Vec2 vec2_sub(Vec2 a, Vec2 b) { return (Vec2){a.x - b.x, a.y - b.y}; }
double vec2_dot(Vec2 a, Vec2 b) { return a.x * b.x + a.y * b.y; }
double vec2_dist_sq(Vec2 a, Vec2 b) { return (a.x - b.x)*(a.x - b.x) + (a.y - b.y)*(a.y - b.y); }
double vec2_dist(Vec2 a, Vec2 b) { return sqrt(vec2_dist_sq(a, b)); }

typedef struct {
    Vec2 points[MAX_VERTICES];
    int count;
} Polygon;

typedef struct {
    char name[32];
    Polygon poly;
    Vec2 circle_center;
    double circle_radius;
    bool is_circular;
    unsigned int flags;       /* Бітова маска KEEPOUT_* */
    int layer;                /* 0 - Top, 1 - Bottom, -1 - All Layers */
} KeepoutZone;

typedef struct {
    char refdes[16];
    Vec2 center;
    double width;
    double height;
    double rotation_deg;
    int layer;
    bool is_mlcc;             /* Прапорець чутливості до згину (MLCC) */
} Component;

typedef struct {
    char net_name[32];
    Vec2 start;
    Vec2 end;
    double width;
    int layer;
} TraceSegment;

typedef struct {
    char object_id[32];
    char rule_name[32];
    char description[128];
    double violation_distance;
} Violation;

/* Тест точки всередині багатокутника (Ray Casting) */
bool point_in_polygon(Vec2 p, const Polygon *poly) {
    if (poly->count < 3) return false;
    bool inside = false;
    for (int i = 0, j = poly->count - 1; i < poly->count; j = i++) {
        if (((poly->points[i].y > p.y) != (poly->points[j].y > p.y)) &&
            (p.x < (poly->points[j].x - poly->points[i].x) * (p.y - poly->points[i].y) /
             (poly->points[j].y - poly->points[i].y) + poly->points[i].x)) {
            inside = !inside;
        }
    }
    return inside;
}

/* Розрахунок чотирьох вершин орієнтованого прямокутника компонента (OBB) */
void get_component_obb(const Component *cmp, Vec2 out_pts[4]) {
    double rad = cmp->rotation_deg * (3.14159265358979323846 / 180.0);
    double cos_a = cos(rad);
    double sin_a = sin(rad);
    double hw = cmp->width / 2.0;
    double hh = cmp->height / 2.0;

    double dx[4] = {-hw,  hw,  hw, -hw};
    double dy[4] = {-hh, -hh,  hh,  hh};

    for (int i = 0; i < 4; i++) {
        out_pts[i].x = cmp->center.x + dx[i] * cos_a - dy[i] * sin_a;
        out_pts[i].y = cmp->center.y + dx[i] * sin_a + dy[i] * cos_a;
    }
}

/* Найкоротша відстань від точки C до відрізка AB */
double dist_point_to_segment(Vec2 c, Vec2 a, Vec2 b) {
    double l2 = vec2_dist_sq(a, b);
    if (l2 < 1e-9) return vec2_dist(c, a);
    double t = vec2_dot(vec2_sub(c, a), vec2_sub(b, a)) / l2;
    if (t < 0.0) t = 0.0;
    else if (t > 1.0) t = 1.0;
    Vec2 projection = (Vec2){a.x + t * (b.x - a.x), a.y + t * (b.y - a.y)};
    return vec2_dist(c, projection);
}

/* Контекст валідатора */
typedef struct {
    Polygon board_outline;
    KeepoutZone keepouts[MAX_KEEPOUTS];
    int keepout_count;
    Violation violations[MAX_VIOLATIONS];
    int violation_count;
} LayoutValidator;

void validator_init(LayoutValidator *v, const Polygon *outline) {
    v->board_outline = *outline;
    v->keepout_count = 0;
    v->violation_count = 0;
}

void validator_add_keepout(LayoutValidator *v, KeepoutZone kz) {
    if (v->keepout_count < MAX_KEEPOUTS) {
        v->keepouts[v->keepout_count++] = kz;
    }
}

void record_violation(LayoutValidator *v, const char *obj, const char *rule, const char *desc, double dist) {
    if (v->violation_count < MAX_VIOLATIONS) {
        Violation *vi = &v->violations[v->violation_count++];
        strncpy(vi->object_id, obj, sizeof(vi->object_id) - 1);
        strncpy(vi->rule_name, rule, sizeof(vi->rule_name) - 1);
        strncpy(vi->description, desc, sizeof(vi->description) - 1);
        vi->violation_distance = dist;
    }
}

/* Аудит компонента */
void validate_component(LayoutValidator *v, const Component *cmp) {
    Vec2 obb[4];
    get_component_obb(cmp, obb);

    /* 1. Перевірка колізій із зонами заборони */
    for (int k = 0; k < v->keepout_count; k++) {
        const KeepoutZone *kz = &v->keepouts[k];
        if (!(kz->flags & KEEPOUT_COMPONENT)) continue;
        if (kz->layer != -1 && kz->layer != cmp->layer) continue;

        if (kz->is_circular) {
            for (int i = 0; i < 4; i++) {
                double d = vec2_dist(obb[i], kz->circle_center);
                if (d < kz->circle_radius) {
                    char desc[128];
                    snprintf(desc, sizeof(desc), "Накладання на зону кріплення '%s' (глибина %.2f мм)", kz->name, kz->circle_radius - d);
                    record_violation(v, cmp->refdes, "Component-Keepout", desc, d);
                    break;
                }
            }
        } else {
            for (int i = 0; i < 4; i++) {
                if (point_in_polygon(obb[i], &kz->poly)) {
                    char desc[128];
                    snprintf(desc, sizeof(desc), "Корпус компонента всередині полігональної зони '%s'", kz->name);
                    record_violation(v, cmp->refdes, "Component-Keepout", desc, 0.0);
                    break;
                }
            }
        }
    }

    /* 2. Контроль відступу до краю плати та ліній депанелізації */
    double min_edge_dist = 1e9;
    for (int i = 0; i < 4; i++) {
        for (int e = 0; e < v->board_outline.count; e++) {
            int next = (e + 1) % v->board_outline.count;
            double d = dist_point_to_segment(obb[i], v->board_outline.points[e], v->board_outline.points[next]);
            if (d < min_edge_dist) min_edge_dist = d;
        }
    }

    double threshold = cmp->is_mlcc ? 3.0 : 1.0;
    if (min_edge_dist < threshold) {
        char desc[128];
        if (cmp->is_mlcc) {
            snprintf(desc, sizeof(desc), "Керамічний MLCC занадто близько до краю плати (%.2f мм < 3.0 мм, ризик тріщин)", min_edge_dist);
            record_violation(v, cmp->refdes, "DFM-Edge-Stress", desc, min_edge_dist);
        } else {
            snprintf(desc, sizeof(desc), "Компонент занадто близько до контуру різання (%.2f мм < 1.0 мм)", min_edge_dist);
            record_violation(v, cmp->refdes, "DFM-Board-Edge", desc, min_edge_dist);
        }
    }
}

/* Аудит друкованої доріжки */
void validate_trace(LayoutValidator *v, const TraceSegment *trace) {
    for (int k = 0; k < v->keepout_count; k++) {
        const KeepoutZone *kz = &v->keepouts[k];
        if (!(kz->flags & KEEPOUT_ROUTE)) continue;
        if (kz->layer != -1 && kz->layer != trace->layer) continue;

        if (kz->is_circular) {
            double eff_r = kz->circle_radius + (trace->width / 2.0);
            if (dist_point_to_segment(kz->circle_center, trace->start, trace->end) <= eff_r) {
                char desc[128];
                snprintf(desc, sizeof(desc), "Провідник net '%s' перетинає зону кріплення '%s'", trace->net_name, kz->name);
                record_violation(v, trace->net_name, "Route-Keepout", desc, 0.0);
            }
        } else {
            Vec2 mid = (Vec2){(trace->start.x + trace->end.x)/2.0, (trace->start.y + trace->end.y)/2.0};
            if (point_in_polygon(trace->start, &kz->poly) ||
                point_in_polygon(trace->end, &kz->poly) ||
                point_in_polygon(mid, &kz->poly)) {
                char desc[128];
                snprintf(desc, sizeof(desc), "Доріжка net '%s' проходить крізь заборонений полігон '%s'", trace->net_name, kz->name);
                record_violation(v, trace->net_name, "Route-Keepout", desc, 0.0);
            }
        }
    }
}

int main(void) {
    Polygon outline = {
        .points = {{0, 0}, {100, 0}, {100, 60}, {0, 60}},
        .count = 4
    };

    LayoutValidator val;
    validator_init(&val, &outline);

    /* Зона 1: Кріпильний отвір M3 у кутку (10, 10), радіус зони заборони 4.0 мм */
    KeepoutZone kz_screw = {
        .name = "M3_Hole_Corner",
        .circle_center = {10.0, 10.0},
        .circle_radius = 4.0,
        .is_circular = true,
        .flags = KEEPOUT_COMPONENT | KEEPOUT_ROUTE | KEEPOUT_COPPER,
        .layer = -1
    };
    validator_add_keepout(&val, kz_screw);

    /* Зона 2: Радіатор TO-220 (Route Keepout 30x20 мм) */
    KeepoutZone kz_heatsink = {
        .name = "TO220_Heatsink_Area",
        .poly = {.points = {{40, 20}, {70, 20}, {70, 40}, {40, 40}}, .count = 4},
        .is_circular = false,
        .flags = KEEPOUT_ROUTE,
        .layer = 0
    };
    validator_add_keepout(&val, kz_heatsink);

    /* Зона 3: Технологічна рейка конвеєра SMT (верхні 4 мм) */
    KeepoutZone kz_rail = {
        .name = "SMT_Top_Rail_4mm",
        .poly = {.points = {{0, 56}, {100, 56}, {100, 60}, {0, 60}}, .count = 4},
        .is_circular = false,
        .flags = KEEPOUT_COMPONENT,
        .layer = 0
    };
    validator_add_keepout(&val, kz_rail);

    /* Тестовий набір елементів топології */
    Component c1 = {
        .refdes = "C1_MLCC_0805",
        .center = {50.0, 1.2},
        .width = 2.0,
        .height = 1.25,
        .rotation_deg = 0.0,
        .layer = 0,
        .is_mlcc = true
    };

    Component r2 = {
        .refdes = "R2_0603",
        .center = {12.0, 10.0},
        .width = 1.6,
        .height = 0.8,
        .rotation_deg = 45.0,
        .layer = 0,
        .is_mlcc = false
    };

    Component led1 = {
        .refdes = "LED_PWR",
        .center = {80.0, 58.0},
        .width = 2.0,
        .height = 1.2,
        .rotation_deg = 0.0,
        .layer = 0,
        .is_mlcc = false
    };

    TraceSegment tr1 = {
        .net_name = "SPI_MISO",
        .start = {35.0, 30.0},
        .end = {75.0, 30.0},
        .width = 0.25,
        .layer = 0
    };

    validate_component(&val, &c1);
    validate_component(&val, &r2);
    validate_component(&val, &led1);
    validate_trace(&val, &tr1);

    printf("=================================================================\n");
    printf("       ЗВІТ АУДИТУ ЗОН ЗАБОРОНИ ТА МЕХАНІЧНИХ ОБМЕЖЕНЬ (C99)    \n");
    printf("=================================================================\n");
    printf("Всього знайдено порушень: %d\n\n", val.violation_count);
    for (int i = 0; i < val.violation_count; i++) {
        Violation *vi = &val.violations[i];
        printf("[%d] Об'єкт: %-16s | Правило: %-18s\n    Деталі: %s\n\n",
               i + 1, vi->object_id, vi->rule_name, vi->description);
    }

    return 0;
}
