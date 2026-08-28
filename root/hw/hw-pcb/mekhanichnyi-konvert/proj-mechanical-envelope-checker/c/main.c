#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define MAX_NAME_LEN 32
#define MAX_COMPONENTS 256
#define MAX_HOLES 32
#define MAX_HEIGHT_ZONES 16
#define MAX_VIOLATIONS 128

typedef enum {
    COMP_CLASS_STANDARD,
    COMP_CLASS_MLCC,         /* Керамічні конденсатори: чутливі до вигину текстоліту */
    COMP_CLASS_CONNECTOR,    /* Роз'єми: потребують перевірки вильоту */
    COMP_CLASS_TALL_PASSIVE  /* Високі котушки/електроліти: блокують інструмент */
} ComponentClass;

typedef enum {
    VIOLATION_SCREW_HEAD_COLLISION,
    VIOLATION_TOOL_CLEARANCE_BLOCKED,
    VIOLATION_MLCC_STRESS_ZONE,
    VIOLATION_HEIGHT_EXCEEDED,
    VIOLATION_CONNECTOR_OVERHANG_MISMATCH
} ViolationType;

typedef struct {
    double x;
    double y;
} Vec2;

typedef struct {
    char refdes[MAX_NAME_LEN];
    ComponentClass comp_class;
    Vec2 center;
    double width;       /* Габарит по осі X при куті 0 (мм) */
    double length;      /* Габарит по осі Y при куті 0 (мм) */
    double height;      /* Висота деталі над платою (мм) */
    double rotation_deg;/* Кут повороту (градуси) */
    double overhang_req;/* Необхідний виліт за плату (якщо роз'єм) */
} Component;

typedef struct {
    char id[MAX_NAME_LEN];
    Vec2 center;
    double drill_dia;
    double screw_head_dia;
    double tool_clearance_dia;
    double mlcc_keepout_dia;
} MountingHole;

typedef struct {
    char name[MAX_NAME_LEN];
    double min_x;
    double min_y;
    double max_x;
    double max_y;
    double max_allowed_height;
} HeightZone;

typedef struct {
    ViolationType type;
    char refdes[MAX_NAME_LEN];
    char context_id[MAX_NAME_LEN];
    double actual_value;
    double limit_value;
    Vec2 location;
} Violation;

typedef struct {
    double board_width;
    double board_height;
    Component components[MAX_COMPONENTS];
    size_t component_count;
    MountingHole holes[MAX_HOLES];
    size_t hole_count;
    HeightZone height_zones[MAX_HEIGHT_ZONES];
    size_t height_zone_count;
    Violation violations[MAX_VIOLATIONS];
    size_t violation_count;
} EnvelopeChecker;

static double deg_to_rad(double deg) {
    return deg * (M_PI / 180.0);
}

static double clamp_val(double val, double min_v, double max_v) {
    if (val < min_v) return min_v;
    if (val > max_v) return max_v;
    return val;
}

/* Перевірка колізії Орієнтованого Прямокутника (OBB) деталі з колом радіуса R */
static bool check_obb_circle_intersect(const Component* c, Vec2 circle_center, double radius, double* out_dist) {
    double rad = deg_to_rad(-c->rotation_deg);
    double cos_a = cos(rad);
    double sin_a = sin(rad);

    double dx = circle_center.x - c->center.x;
    double dy = circle_center.y - c->center.y;

    /* Локальні координати центру кола відносно центру компонента */
    double local_x = dx * cos_a - dy * sin_a;
    double local_y = dx * sin_a + dy * cos_a;

    double half_w = c->width * 0.5;
    double half_l = c->length * 0.5;

    double nearest_x = clamp_val(local_x, -half_w, half_w);
    double nearest_y = clamp_val(local_y, -half_l, half_l);

    double delta_x = local_x - nearest_x;
    double delta_y = local_y - nearest_y;

    double dist_sq = delta_x * delta_x + delta_y * delta_y;
    double dist = sqrt(dist_sq);

    if (out_dist) {
        *out_dist = dist;
    }

    return dist_sq < (radius * radius);
}

void envelope_checker_init(EnvelopeChecker* chk, double board_w, double board_h) {
    memset(chk, 0, sizeof(EnvelopeChecker));
    chk->board_width = board_w;
    chk->board_height = board_h;
}

bool envelope_checker_add_component(EnvelopeChecker* chk, const Component* comp) {
    if (chk->component_count >= MAX_COMPONENTS) return false;
    chk->components[chk->component_count++] = *comp;
    return true;
}

bool envelope_checker_add_hole(EnvelopeChecker* chk, const MountingHole* hole) {
    if (chk->hole_count >= MAX_HOLES) return false;
    chk->holes[chk->hole_count++] = *hole;
    return true;
}

bool envelope_checker_add_height_zone(EnvelopeChecker* chk, const HeightZone* zone) {
    if (chk->height_zone_count >= MAX_HEIGHT_ZONES) return false;
    chk->height_zones[chk->height_zone_count++] = *zone;
    return true;
}

static void log_violation(EnvelopeChecker* chk, ViolationType type, const char* ref, const char* ctx, double act, double lim, Vec2 loc) {
    if (chk->violation_count >= MAX_VIOLATIONS) return;
    Violation* v = &chk->violations[chk->violation_count++];
    v->type = type;
    strncpy(v->refdes, ref, MAX_NAME_LEN - 1);
    strncpy(v->context_id, ctx, MAX_NAME_LEN - 1);
    v->actual_value = act;
    v->limit_value = lim;
    v->location = loc;
}

void envelope_checker_run(EnvelopeChecker* chk) {
    chk->violation_count = 0;

    for (size_t i = 0; i < chk->component_count; ++i) {
        const Component* c = &chk->components[i];

        /* 1. Перевірка відносно кожного кріпильного отвору */
        for (size_t h = 0; h < chk->hole_count; ++h) {
            const MountingHole* hole = &chk->holes[h];
            double dist = 0.0;

            /* А. Головка гвинта / прямий механічний контакт */
            double r_screw = hole->screw_head_dia * 0.5;
            if (check_obb_circle_intersect(c, hole->center, r_screw, &dist)) {
                log_violation(chk, VIOLATION_SCREW_HEAD_COLLISION, c->refdes, hole->id, dist, r_screw, c->center);
            }

            /* Б. Зона проходу викрутки/ключа для високих деталей (h > 4.0 мм) */
            double r_tool = hole->tool_clearance_dia * 0.5;
            if (c->height > 4.0 && check_obb_circle_intersect(c, hole->center, r_tool, &dist)) {
                log_violation(chk, VIOLATION_TOOL_CLEARANCE_BLOCKED, c->refdes, hole->id, c->height, r_tool, c->center);
            }

            /* В. Зона деформаційного стресу для MLCC */
            if (c->comp_class == COMP_CLASS_MLCC) {
                double r_mlcc = hole->mlcc_keepout_dia * 0.5;
                if (check_obb_circle_intersect(c, hole->center, r_mlcc, &dist)) {
                    log_violation(chk, VIOLATION_MLCC_STRESS_ZONE, c->refdes, hole->id, dist, r_mlcc, c->center);
                }
            }
        }

        /* 2. Перевірка висотних зон корпусу */
        for (size_t z = 0; z < chk->height_zone_count; ++z) {
            const HeightZone* zone = &chk->height_zones[z];
            /* Спрощена перевірка потрапляння центру деталі у висотну зону */
            if (c->center.x >= zone->min_x && c->center.x <= zone->max_x &&
                c->center.y >= zone->min_y && c->center.y <= zone->max_y) {
                if (c->height > zone->max_allowed_height) {
                    log_violation(chk, VIOLATION_HEIGHT_EXCEEDED, c->refdes, zone->name, c->height, zone->max_allowed_height, c->center);
                }
            }
        }

        /* 3. Перевірка вильоту роз'єму на лівому боці плати (x = 0) */
        if (c->comp_class == COMP_CLASS_CONNECTOR && c->overhang_req > 0.0) {
            double actual_left_edge = c->center.x - (c->length * 0.5); /* якщо роз'єм вздовж X */
            double actual_overhang = -actual_left_edge; /* виступ за 0 */
            if (fabs(actual_overhang - c->overhang_req) > 0.3) {
                log_violation(chk, VIOLATION_CONNECTOR_OVERHANG_MISMATCH, c->refdes, "LeftEdge", actual_overhang, c->overhang_req, c->center);
            }
        }
    }
}

void envelope_checker_print_report(const EnvelopeChecker* chk) {
    printf("===============================================================\n");
    printf("ЗВІТ МЕХАНІЧНОГО КОНВЕРТА: Перевірено %zu деталей, %zu отворів\n", chk->component_count, chk->hole_count);
    printf("Знайдено дефектів: %zu\n", chk->violation_count);
    printf("===============================================================\n");

    for (size_t i = 0; i < chk->violation_count; ++i) {
        const Violation* v = &chk->violations[i];
        printf("[%02zu] ", i + 1);
        switch (v->type) {
            case VIOLATION_SCREW_HEAD_COLLISION:
                printf("КОЛІЗІЯ З ГОЛОВКОЮ ГВИНТА: %s перекриває %s (відстань %.2f мм < R_screw %.2f мм)\n",
                       v->refdes, v->context_id, v->actual_value, v->limit_value);
                break;
            case VIOLATION_TOOL_CLEARANCE_BLOCKED:
                printf("БЛОКУВАННЯ ІНСТРУМЕНТУ: Деталь %s (висота %.2f мм) блокує зону монтажу %s (R %.2f мм)\n",
                       v->refdes, v->actual_value, v->context_id, v->limit_value);
                break;
            case VIOLATION_MLCC_STRESS_ZONE:
                printf("НЕБЕЗПЕКА ЗЛАМУ MLCC: Конденсатор %s у зоні деформацій %s (відстань %.2f мм < R_keepout %.2f мм)\n",
                       v->refdes, v->context_id, v->actual_value, v->limit_value);
                break;
            case VIOLATION_HEIGHT_EXCEEDED:
                printf("ПЕРЕВИЩЕННЯ ВИСОТИ КОРПУСУ: %s має висоту %.2f мм > ліміту %.2f мм у зоні %s\n",
                       v->refdes, v->actual_value, v->limit_value, v->context_id);
                break;
            case VIOLATION_CONNECTOR_OVERHANG_MISMATCH:
                printf("ПОХИБКА ВИЛЬОТУ РОЗ'ЄМУ: %s виступає на %.2f мм (вимога %.2f мм) на %s\n",
                       v->refdes, v->actual_value, v->limit_value, v->context_id);
                break;
        }
    }
    printf("===============================================================\n");
}

int main(void) {
    EnvelopeChecker checker;
    envelope_checker_init(&checker, 120.0, 70.0);

    /* Додаємо 4 кріпильні отвори під M3 */
    MountingHole h1 = { "H1_TopLeft", { 6.0, 64.0 }, 3.2, 6.0, 8.0, 10.0 };
    MountingHole h2 = { "H2_TopRight", { 114.0, 64.0 }, 3.2, 6.0, 8.0, 10.0 };
    MountingHole h3 = { "H3_BotLeft", { 6.0, 6.0 }, 3.2, 6.0, 8.0, 10.0 };
    MountingHole h4 = { "H4_BotRight", { 114.0, 6.0 }, 3.2, 6.0, 8.0, 10.0 };

    envelope_checker_add_hole(&checker, &h1);
    envelope_checker_add_hole(&checker, &h2);
    envelope_checker_add_hole(&checker, &h3);
    envelope_checker_add_hole(&checker, &h4);

    /* Додаємо низькопрофільну зону корпусу під ребром жорсткості */
    HeightZone rib_zone = { "TopRib_Shield", 30.0, 50.0, 90.0, 70.0, 3.5 };
    envelope_checker_add_height_zone(&checker, &rib_zone);

    /* Тестові деталі */
    Component c1 = { "C101", COMP_CLASS_MLCC, { 7.5, 61.5 }, 1.6, 0.8, 0.9, 45.0, 0.0 }; /* Поруч із H1: небезпека MLCC */
    Component l1 = { "L201", COMP_CLASS_TALL_PASSIVE, { 9.0, 6.0 }, 6.0, 6.0, 5.5, 0.0, 0.0 }; /* Блокує ключ біля H3 */
    Component j1 = { "J1_USB", COMP_CLASS_CONNECTOR, { 4.0, 35.0 }, 8.9, 10.0, 3.2, 0.0, 1.4 }; /* USB-C виліт */
    Component q1 = { "Q301", COMP_CLASS_STANDARD, { 50.0, 60.0 }, 6.5, 6.5, 4.2, 0.0, 0.0 }; /* Зависокий транзистор у зоні ребра */

    envelope_checker_add_component(&checker, &c1);
    envelope_checker_add_component(&checker, &l1);
    envelope_checker_add_component(&checker, &j1);
    envelope_checker_add_component(&checker, &q1);

    envelope_checker_run(&checker);
    envelope_checker_print_report(&checker);

    return 0;
}
