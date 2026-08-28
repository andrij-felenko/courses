/*
 * dfm_parser.c — Модуль геометричного аудиту технологічності плати (C99).
 * Виконує аналіз векторних примітивів, кутів, поясів та контурних зазорів.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef enum {
    SEV_INFO = 0,
    SEV_WARNING = 1,
    SEV_CRITICAL = 2
} severity_t;

typedef enum {
    DEFECT_NONE = 0,
    DEFECT_ACID_TRAP,
    DEFECT_MASK_SLIVER,
    DEFECT_ANNULAR_BREAKOUT,
    DEFECT_ANNULAR_TANGENCY,
    DEFECT_COPPER_TO_EDGE
} defect_type_t;

typedef struct {
    double x;
    double y;
} point2d_t;

typedef struct {
    point2d_t start;
    point2d_t end;
    double width_mm;
    char net_name[32];
} trace_segment_t;

typedef struct {
    point2d_t center;
    double pad_dia_mm;
    double drill_dia_mm;
    char net_name[32];
} via_element_t;

typedef struct {
    point2d_t center;
    double width_mm;
    double height_mm;
    char refdes[16];
} mask_aperture_t;

typedef struct {
    point2d_t p1;
    point2d_t p2;
} outline_segment_t;

typedef struct {
    double min_trace_width_mm;
    double min_trace_clearance_mm;
    double min_mask_sliver_mm;
    double min_annular_ring_mm;
    double min_copper_to_edge_mm;
    double max_acute_angle_deg;
    double drill_runout_tolerance_mm;
    double drill_plating_allowance_mm;
} dfm_rules_config_t;

typedef struct {
    defect_type_t type;
    severity_t severity;
    point2d_t location;
    char description[128];
    char recommendation[128];
} dfm_issue_t;

static double vec_length(point2d_t v) {
    return sqrt(v.x * v.x + v.y * v.y);
}

static double compute_vector_angle_deg(point2d_t v1, point2d_t v2) {
    double l1 = vec_length(v1);
    double l2 = vec_length(v2);
    if (l1 < 1e-6 || l2 < 1e-6) return 180.0;

    double dot = v1.x * v2.x + v1.y * v2.y;
    double cos_val = dot / (l1 * l2);

    if (cos_val > 1.0) cos_val = 1.0;
    if (cos_val < -1.0) cos_val = -1.0;

    return acos(cos_val) * (180.0 / M_PI);
}

static double point_to_segment_distance(point2d_t pt, outline_segment_t seg) {
    double dx = seg.p2.x - seg.p1.x;
    double dy = seg.p2.y - seg.p1.y;
    double len_sq = dx * dx + dy * dy;

    if (len_sq < 1e-9) {
        double px = pt.x - seg.p1.x;
        double py = pt.y - seg.p1.y;
        return sqrt(px * px + py * py);
    }

    double t = ((pt.x - seg.p1.x) * dx + (pt.y - seg.p1.y) * dy) / len_sq;
    if (t < 0.0) t = 0.0;
    if (t > 1.0) t = 1.0;

    double near_x = seg.p1.x + t * dx;
    double near_y = seg.p1.y + t * dy;

    double rx = pt.x - near_x;
    double ry = pt.y - near_y;
    return sqrt(rx * rx + ry * ry);
}

int audit_acid_traps(const trace_segment_t *traces, size_t count,
                     const dfm_rules_config_t *cfg, dfm_issue_t *issues, int max_issues) {
    int found = 0;
    for (size_t i = 0; i < count; i++) {
        for (size_t j = i + 1; j < count; j++) {
            if (found >= max_issues) return found;

            bool connected = false;
            point2d_t vertex;
            point2d_t v1, v2;

            if (fabs(traces[i].start.x - traces[j].start.x) < 1e-4 &&
                fabs(traces[i].start.y - traces[j].start.y) < 1e-4) {
                connected = true;
                vertex = traces[i].start;
                v1 = (point2d_t){traces[i].end.x - vertex.x, traces[i].end.y - vertex.y};
                v2 = (point2d_t){traces[j].end.x - vertex.x, traces[j].end.y - vertex.y};
            } else if (fabs(traces[i].end.x - traces[j].start.x) < 1e-4 &&
                       fabs(traces[i].end.y - traces[j].start.y) < 1e-4) {
                connected = true;
                vertex = traces[i].end;
                v1 = (point2d_t){traces[i].start.x - vertex.x, traces[i].start.y - vertex.y};
                v2 = (point2d_t){traces[j].end.x - vertex.x, traces[j].end.y - vertex.y};
            } else if (fabs(traces[i].end.x - traces[j].end.x) < 1e-4 &&
                       fabs(traces[i].end.y - traces[j].end.y) < 1e-4) {
                connected = true;
                vertex = traces[i].end;
                v1 = (point2d_t){traces[i].start.x - vertex.x, traces[i].start.y - vertex.y};
                v2 = (point2d_t){traces[j].end.x - vertex.x, traces[j].end.y - vertex.y};
            }

            if (connected) {
                double angle = compute_vector_angle_deg(v1, v2);
                if (angle < cfg->max_acute_angle_deg) {
                    dfm_issue_t *iss = &issues[found++];
                    iss->type = DEFECT_ACID_TRAP;
                    iss->severity = SEV_WARNING;
                    iss->location = vertex;
                    snprintf(iss->description, sizeof(iss->description),
                             "Гострий кут трасування: %.1f deg (поріг %.1f deg) у ланцюзі %s",
                             angle, cfg->max_acute_angle_deg, traces[i].net_name);
                    snprintf(iss->recommendation, sizeof(iss->recommendation),
                             "Збільште кут сходження або застосуйте скруглення кутів (filleting)");
                }
            }
        }
    }
    return found;
}

int audit_annular_rings(const via_element_t *vias, size_t count,
                        const dfm_rules_config_t *cfg, dfm_issue_t *issues, int max_issues) {
    int found = 0;
    for (size_t i = 0; i < count; i++) {
        if (found >= max_issues) return found;

        double tool_drill = vias[i].drill_dia_mm + cfg->drill_plating_allowance_mm;
        double nominal_ar = (vias[i].pad_dia_mm - tool_drill) / 2.0;
        double worst_case_ar = nominal_ar - cfg->drill_runout_tolerance_mm;

        if (worst_case_ar < 0.0) {
            dfm_issue_t *iss = &issues[found++];
            iss->type = DEFECT_ANNULAR_BREAKOUT;
            iss->severity = SEV_CRITICAL;
            iss->location = vias[i].center;
            snprintf(iss->description, sizeof(iss->description),
                     "Прорив пояска переходу (Breakout): пад %.2f мм, отвір %.2f мм (дефіцит %.3f мм)",
                     vias[i].pad_dia_mm, tool_drill, -worst_case_ar);
            snprintf(iss->recommendation, sizeof(iss->recommendation),
                     "Збільште діаметр мідного майданчика або додайте Teardrop");
        } else if (worst_case_ar < cfg->min_annular_ring_mm) {
            dfm_issue_t *iss = &issues[found++];
            iss->type = DEFECT_ANNULAR_TANGENCY;
            iss->severity = SEV_WARNING;
            iss->location = vias[i].center;
            snprintf(iss->description, sizeof(iss->description),
                     "Поясок менший за вимоги IPC Class 3: залишок %.3f мм (норма %.2f мм)",
                     worst_case_ar, cfg->min_annular_ring_mm);
            snprintf(iss->recommendation, sizeof(iss->recommendation),
                     "Збільште розмір майданчика на 0.05-0.10 мм");
        }
    }
    return found;
}

int audit_copper_to_edge(const via_element_t *vias, size_t via_count,
                         const outline_segment_t *outline, size_t seg_count,
                         const dfm_rules_config_t *cfg, dfm_issue_t *issues, int max_issues) {
    int found = 0;
    for (size_t i = 0; i < via_count; i++) {
        double min_dist = 1e9;
        for (size_t s = 0; s < seg_count; s++) {
            double d = point_to_segment_distance(vias[i].center, outline[s]);
            if (d < min_dist) min_dist = d;
        }

        double copper_clearance = min_dist - (vias[i].pad_dia_mm / 2.0);
        if (copper_clearance < cfg->min_copper_to_edge_mm) {
            if (found >= max_issues) return found;
            dfm_issue_t *iss = &issues[found++];
            iss->type = DEFECT_COPPER_TO_EDGE;
            iss->severity = SEV_CRITICAL;
            iss->location = vias[i].center;
            snprintf(iss->description, sizeof(iss->description),
                     "Мідь занадто близько до контуру: зазор %.3f мм (норма >= %.2f мм)",
                     copper_clearance, cfg->min_copper_to_edge_mm);
            snprintf(iss->recommendation, sizeof(iss->recommendation),
                     "Зсуньте елемент усередину плати на >= %.3f мм від лінії фрезерування",
                     cfg->min_copper_to_edge_mm - copper_clearance);
        }
    }
    return found;
}

void output_console_report(const dfm_issue_t *issues, int count) {
    printf("=================================================================\n");
    printf("                  РЕЗУЛЬТАТИ АУДИТУ ТЕХНОЛОГІЧНОСТІ DFM          \n");
    printf("=================================================================\n");

    if (count == 0) {
        printf(" [OK] Топологія відповідає всім заданим технологічним нормам.\n");
        printf("=================================================================\n");
        return;
    }

    int crit_count = 0;
    int warn_count = 0;

    for (int i = 0; i < count; i++) {
        const char *tag = "INFO";
        if (issues[i].severity == SEV_CRITICAL) {
            tag = "CRITICAL";
            crit_count++;
        } else if (issues[i].severity == SEV_WARNING) {
            tag = "WARNING";
            warn_count++;
        }

        printf("[%s] Порушення #%d у точці (X: %.2f, Y: %.2f)\n",
               tag, i + 1, issues[i].location.x, issues[i].location.y);
        printf("  Суть:  %s\n", issues[i].description);
        printf("  Усунення: %s\n\n", issues[i].recommendation);
    }

    printf("-----------------------------------------------------------------\n");
    printf("Всього знайдено: %d критичних помилок, %d попереджень надійності.\n",
           crit_count, warn_count);
    printf("=================================================================\n");
}

int main(void) {
    dfm_rules_config_t config = {
        .min_trace_width_mm = 0.10,
        .min_trace_clearance_mm = 0.10,
        .min_mask_sliver_mm = 0.09,
        .min_annular_ring_mm = 0.05,
        .min_copper_to_edge_mm = 0.30,
        .max_acute_angle_deg = 85.0,
        .drill_runout_tolerance_mm = 0.04,
        .drill_plating_allowance_mm = 0.10
    };

    trace_segment_t sample_traces[] = {
        {{12.0, 15.0}, {25.0, 25.0}, 0.15, "NET_SPI_MOSI"},
        {{25.0, 25.0}, {28.0, 16.0}, 0.15, "NET_SPI_MOSI"}
    };

    via_element_t sample_vias[] = {
        {{30.0, 40.0}, 0.45, 0.30, "NET_VDD_IO"},
        {{49.85, 25.0}, 0.50, 0.30, "NET_GND"}
    };

    outline_segment_t sample_outline[] = {
        {{0.0, 0.0}, {50.0, 0.0}},
        {{50.0, 0.0}, {50.0, 50.0}},
        {{50.0, 50.0}, {0.0, 50.0}},
        {{0.0, 50.0}, {0.0, 0.0}}
    };

    dfm_issue_t issues_buffer[32];
    int issue_count = 0;

    issue_count += audit_acid_traps(sample_traces, sizeof(sample_traces)/sizeof(sample_traces[0]),
                                    &config, issues_buffer + issue_count, 32 - issue_count);
    issue_count += audit_annular_rings(sample_vias, sizeof(sample_vias)/sizeof(sample_vias[0]),
                                      &config, issues_buffer + issue_count, 32 - issue_count);
    issue_count += audit_copper_to_edge(sample_vias, sizeof(sample_vias)/sizeof(sample_vias[0]),
                                       sample_outline, sizeof(sample_outline)/sizeof(sample_outline[0]),
                                       &config, issues_buffer + issue_count, 32 - issue_count);

    output_console_report(issues_buffer, issue_count);
    return 0;
}
