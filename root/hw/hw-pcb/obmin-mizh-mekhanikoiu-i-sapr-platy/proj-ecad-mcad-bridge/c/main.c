#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define MAX_VERTICES 256
#define MAX_HOLES 64
#define MAX_ERRORS 128
#define EPSILON_CLOSURE 0.05
#define EPSILON_HOLE_POS 0.08
#define EPSILON_HOLE_DIA 0.05
#define M_PI_VAL 3.14159265358979323846

typedef struct {
    double x;
    double y;
} Point2D;

typedef struct {
    double x;
    double y;
    double z;
} Point3D;

typedef struct {
    Point2D pt;
    double bulge; // 0.0 = прямий відрізок, tan(theta/4) для дуги
} PolyVertex;

typedef struct {
    PolyVertex vertices[MAX_VERTICES];
    size_t count;
    bool is_closed;
} DxfPolyline;

typedef struct {
    Point2D center;
    double diameter;
    char label[16];
} MountingHole;

typedef struct {
    DxfPolyline outline;
    MountingHole holes[MAX_HOLES];
    size_t hole_count;
    double min_x, min_y, max_x, max_y;
} CadBoard2D;

typedef struct {
    Point3D vertices[MAX_VERTICES];
    size_t vertex_count;
    MountingHole holes[MAX_HOLES];
    size_t hole_count;
    double thickness;
    double min_x, min_y, max_x, max_y;
} StepBoard3D;

typedef enum {
    SEV_INFO = 0,
    SEV_WARNING,
    SEV_ERROR
} Severity;

typedef struct {
    Severity severity;
    char message[128];
    double expected;
    double actual;
    double delta;
} ValidationIssue;

typedef struct {
    ValidationIssue issues[MAX_ERRORS];
    size_t count;
    bool passed;
} ValidationReport;

static void report_add(ValidationReport *rep, Severity sev, const char *msg, double exp_v, double act_v) {
    if (rep->count >= MAX_ERRORS) return;
    ValidationIssue *iss = &rep->issues[rep->count++];
    iss->severity = sev;
    strncpy(iss->message, msg, sizeof(iss->message) - 1);
    iss->message[sizeof(iss->message) - 1] = '\0';
    iss->expected = exp_v;
    iss->actual = act_v;
    iss->delta = fabs(act_v - exp_v);
    if (sev == SEV_ERROR) {
        rep->passed = false;
    }
}

static double distance_2d(Point2D a, Point2D b) {
    double dx = b.x - a.x;
    double dy = b.y - a.y;
    return sqrt(dx * dx + dy * dy);
}

static void calculate_bbox_2d(CadBoard2D *board) {
    if (board->outline.count == 0) return;
    board->min_x = board->outline.vertices[0].pt.x;
    board->max_x = board->min_x;
    board->min_y = board->outline.vertices[0].pt.y;
    board->max_y = board->min_y;

    for (size_t i = 1; i < board->outline.count; ++i) {
        Point2D p = board->outline.vertices[i].pt;
        if (p.x < board->min_x) board->min_x = p.x;
        if (p.x > board->max_x) board->max_x = p.x;
        if (p.y < board->min_y) board->min_y = p.y;
        if (p.y > board->max_y) board->max_y = p.y;
    }
}

static void calculate_bbox_3d(StepBoard3D *board) {
    if (board->vertex_count == 0) return;
    board->min_x = board->vertices[0].x;
    board->max_x = board->min_x;
    board->min_y = board->vertices[0].y;
    board->max_y = board->min_y;

    for (size_t i = 1; i < board->vertex_count; ++i) {
        Point3D p = board->vertices[i];
        if (p.x < board->min_x) board->min_x = p.x;
        if (p.x > board->max_x) board->max_x = p.x;
        if (p.y < board->min_y) board->min_y = p.y;
        if (p.y > board->max_y) board->max_y = p.y;
    }
}

static double calculate_polygon_area(const CadBoard2D *board) {
    if (board->outline.count < 3) return 0.0;
    double area = 0.0;
    size_t n = board->outline.count;
    for (size_t i = 0; i < n; ++i) {
        size_t next = (i + 1) % n;
        Point2D p1 = board->outline.vertices[i].pt;
        Point2D p2 = board->outline.vertices[next].pt;
        area += (p1.x * p2.y - p2.x * p1.y);
    }
    return area * 0.5;
}

static void validate_contour_closure(const CadBoard2D *board, ValidationReport *rep) {
    if (board->outline.count < 3) {
        report_add(rep, SEV_ERROR, "DXF Outline: недостатня кількість вершин контуру (<3)", 3.0, (double)board->outline.count);
        return;
    }
    Point2D first = board->outline.vertices[0].pt;
    Point2D last = board->outline.vertices[board->outline.count - 1].pt;
    double gap = distance_2d(first, last);

    if (gap > EPSILON_CLOSURE) {
        report_add(rep, SEV_ERROR, "DXF Outline: розімкнений контур друкованої плати", 0.0, gap);
    } else {
        report_add(rep, SEV_INFO, "DXF Outline: контур коректно замкнений", 0.0, gap);
    }

    double area = calculate_polygon_area(board);
    if (area <= 0.0) {
        report_add(rep, SEV_WARNING, "DXF Outline: полігон має від'ємну орієнтацію (CW замість CCW)", 1.0, area);
    }
}

static void validate_bounding_boxes(const CadBoard2D *dxf, const StepBoard3D *step, ValidationReport *rep) {
    double dxf_w = dxf->max_x - dxf->min_x;
    double dxf_h = dxf->max_y - dxf->min_y;
    double step_w = step->max_x - step->min_x;
    double step_h = step->max_y - step->min_y;

    if (fabs(dxf_w - step_w) > EPSILON_CLOSURE) {
        report_add(rep, SEV_ERROR, "BBox Mismatch: розбіжність ширини плати (X)", dxf_w, step_w);
    } else {
        report_add(rep, SEV_INFO, "BBox Width: ширина збігається в межах допуску", dxf_w, step_w);
    }

    if (fabs(dxf_h - step_h) > EPSILON_CLOSURE) {
        report_add(rep, SEV_ERROR, "BBox Mismatch: розбіжність висоти плати (Y)", dxf_h, step_h);
    } else {
        report_add(rep, SEV_INFO, "BBox Height: висота збігається в межах допуску", dxf_h, step_h);
    }
}

static void validate_mounting_holes(const CadBoard2D *dxf, const StepBoard3D *step, ValidationReport *rep) {
    if (dxf->hole_count != step->hole_count) {
        report_add(rep, SEV_ERROR, "Holes Count: різна кількість кріпильних отворів у DXF та STEP",
                   (double)dxf->hole_count, (double)step->hole_count);
    }

    for (size_t i = 0; i < dxf->hole_count; ++i) {
        const MountingHole *dh = &dxf->holes[i];
        bool matched = false;

        for (size_t j = 0; j < step->hole_count; ++j) {
            const MountingHole *sh = &step->holes[j];
            double pos_delta = distance_2d(dh->center, sh->center);

            if (pos_delta <= EPSILON_HOLE_POS) {
                matched = true;
                double dia_delta = fabs(dh->diameter - sh->diameter);
                if (dia_delta > EPSILON_HOLE_DIA) {
                    char buf[128];
                    snprintf(buf, sizeof(buf), "Hole %s (%s): розбіжність діаметра отвору", dh->label, sh->label);
                    report_add(rep, SEV_WARNING, buf, dh->diameter, sh->diameter);
                } else {
                    char buf[128];
                    snprintf(buf, sizeof(buf), "Hole %s: співвісність та діаметр підтверджено", dh->label);
                    report_add(rep, SEV_INFO, buf, 0.0, pos_delta);
                }
                break;
            }
        }

        if (!matched) {
            char buf[128];
            snprintf(buf, sizeof(buf), "Hole %s: отвір із DXF відсутній у 3D моделі STEP", dh->label);
            report_add(rep, SEV_ERROR, buf, 0.0, 1.0);
        }
    }
}

void print_validation_summary(const ValidationReport *rep) {
    printf("=================================================================\n");
    printf("     ЗВІТ ВАЛІДАЦІЇ ГЕОМЕТРІЇ: 2D DXF OUTLINE <-> 3D STEP        \n");
    printf("=================================================================\n");
    for (size_t i = 0; i < rep->count; ++i) {
        const ValidationIssue *iss = &rep->issues[i];
        const char *sev_str = "[INFO]";
        if (iss->severity == SEV_WARNING) sev_str = "[WARN]";
        if (iss->severity == SEV_ERROR) sev_str = "[FAIL]";

        printf("%-7s %-55s\n", sev_str, iss->message);
        if (iss->severity != SEV_INFO || iss->delta > 0.0001) {
            printf("        Очікувано: %8.3f мм | Фактично: %8.3f мм | Відхилення: %8.3f мм\n",
                   iss->expected, iss->actual, iss->delta);
        }
    }
    printf("-----------------------------------------------------------------\n");
    if (rep->passed) {
        printf("РЕЗУЛЬТАТ: УСПІХ — 2D контур повністю узгоджений із 3D моделлю STEP.\n");
    } else {
        printf("РЕЗУЛЬТАТ: КРИТИЧНІ ПОМИЛКИ — виявлено геометричну несумісність!\n");
    }
    printf("=================================================================\n");
}

int main(void) {
    // 1. Ініціалізація еталонної 2D плати з DXF
    CadBoard2D dxf_board = {0};
    dxf_board.outline.vertices[0] = (PolyVertex){{0.0, 0.0}, 0.0};
    dxf_board.outline.vertices[1] = (PolyVertex){{100.0, 0.0}, 0.41421356}; // Bulge R=2.0 mm кут
    dxf_board.outline.vertices[2] = (PolyVertex){{100.0, 60.0}, 0.0};
    dxf_board.outline.vertices[3] = (PolyVertex){{0.0, 60.0}, 0.0};
    dxf_board.outline.vertices[4] = (PolyVertex){{0.0, 0.0}, 0.0}; // Замикання
    dxf_board.outline.count = 5;
    dxf_board.outline.is_closed = true;

    // Кріпильні отвори M3
    dxf_board.holes[0] = (MountingHole){{4.0, 4.0}, 3.2, "H1"};
    dxf_board.holes[1] = (MountingHole){{96.0, 4.0}, 3.2, "H2"};
    dxf_board.holes[2] = (MountingHole){{96.0, 56.0}, 3.2, "H3"};
    dxf_board.holes[3] = (MountingHole){{4.0, 56.0}, 3.2, "H4"};
    dxf_board.hole_count = 4;
    calculate_bbox_2d(&dxf_board);

    // 2. Ініціалізація 3D плати, імпортованої зі STEP (симуляція з мікропохибкою H2)
    StepBoard3D step_board = {0};
    step_board.vertices[0] = (Point3D){0.0, 0.0, 0.0};
    step_board.vertices[1] = (Point3D){100.0, 0.0, 0.0};
    step_board.vertices[2] = (Point3D){100.0, 60.0, 0.0};
    step_board.vertices[3] = (Point3D){0.0, 60.0, 0.0};
    step_board.vertex_count = 4;
    step_board.thickness = 1.6;

    step_board.holes[0] = (MountingHole){{4.0, 4.0}, 3.2, "STEP_H1"};
    step_board.holes[1] = (MountingHole){{96.12, 4.0}, 3.2, "STEP_H2"}; // Зсув +0.12 мм!
    step_board.holes[2] = (MountingHole){{96.0, 56.0}, 3.2, "STEP_H3"};
    step_board.holes[3] = (MountingHole){{4.0, 56.0}, 3.2, "STEP_H4"};
    step_board.hole_count = 4;
    calculate_bbox_3d(&step_board);

    // 3. Запуск конвеєра валідації
    ValidationReport report = {0};
    report.passed = true;

    validate_contour_closure(&dxf_board, &report);
    validate_bounding_boxes(&dxf_board, &step_board, &report);
    validate_mounting_holes(&dxf_board, &step_board, &report);

    // 4. Друк підсумкового звіту
    print_validation_summary(&report);

    return report.passed ? EXIT_SUCCESS : EXIT_FAILURE;
}
