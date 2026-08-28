#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

// Точка на площині
typedef struct {
    double x;
    double y;
} Point;

// Відрізок із унікальним ідентифікатором
typedef struct {
    int id;
    Point p1; // лівий кінець (p1.x <= p2.x)
    Point p2; // правий кінець
} Segment;

// Типи подій замітальної прямої
typedef enum {
    EVENT_START,
    EVENT_END,
    EVENT_INTERSECT
} EventType;

// Подія в черзі
typedef struct {
    double x;
    double y;
    EventType type;
    int seg1_id;
    int seg2_id; // використовується лише для EVENT_INTERSECT
} Event;

// Предикат орієнтації (косий добуток векторів AB та AC)
// > 0: лівий поворот (CCW), < 0: правий (CW), == 0: колінеарні
double orientation(Point a, Point b, Point c) {
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
}

// Перевірка чи лежить точка q на відрізку pr (для колінеарних точок)
bool on_segment(Point p, Point q, Point r) {
    return q.x <= fmax(p.x, r.x) && q.x >= fmin(p.x, r.x) &&
           q.y <= fmax(p.y, r.y) && q.y >= fmin(p.y, r.y);
}

// Перевірка перетину двох відрізків
bool segments_intersect(Segment s1, Segment s2, Point *out_pt) {
    Point a = s1.p1, b = s1.p2;
    Point c = s2.p1, d = s2.p2;

    double d1 = orientation(a, b, c);
    double d2 = orientation(a, b, d);
    double d3 = orientation(c, d, a);
    double d4 = orientation(c, d, b);

    // Загальний випадок строгого перетину
    if (((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) &&
        ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0))) {
        if (out_pt) {
            // Обчислення точки перетину за правилом Крамера
            double a1 = b.y - a.y;
            double b1 = a.x - b.x;
            double c1 = a1 * a.x + b1 * a.y;

            double a2 = d.y - c.y;
            double b2 = c.x - d.x;
            double c2 = a2 * c.x + b2 * c.y;

            double det = a1 * b2 - a2 * b1;
            if (fabs(det) > 1e-9) {
                out_pt->x = (b2 * c1 - b1 * c2) / det;
                out_pt->y = (a1 * c2 - a2 * c1) / det;
            }
        }
        return true;
    }

    // Крайові випадки колінеарності
    if (fabs(d1) < 1e-9 && on_segment(a, c, b)) { if (out_pt) *out_pt = c; return true; }
    if (fabs(d2) < 1e-9 && on_segment(a, d, b)) { if (out_pt) *out_pt = d; return true; }
    if (fabs(d3) < 1e-9 && on_segment(c, a, d)) { if (out_pt) *out_pt = a; return true; }
    if (fabs(d4) < 1e-9 && on_segment(c, b, d)) { if (out_pt) *out_pt = b; return true; }

    return false;
}

// Обчислення y-координати відрізка при заданому x для структури статусу
double get_segment_y(Segment s, double current_x) {
    if (fabs(s.p2.x - s.p1.x) < 1e-9) return s.p1.y;
    double t = (current_x - s.p1.x) / (s.p2.x - s.p1.x);
    return s.p1.y + t * (s.p2.y - s.p1.y);
}

// Компаратор подій для сортування за X, потім за Y
int compare_events(const void *a, const void *b) {
    const Event *ea = (const Event *)a;
    const Event *eb = (const Event *)b;
    if (fabs(ea->x - eb->x) > 1e-9) {
        return (ea->x > eb->x) ? 1 : -1;
    }
    // При однаковому X: End < Intersect < Start
    if (ea->type != eb->type) {
        return ea->type - eb->type;
    }
    return (ea->y > eb->y) ? 1 : -1;
}

// Демонстрація запуску замітальної прямої
int main(void) {
    Segment segs[] = {
        {0, {1.0, 1.0}, {5.0, 5.0}},
        {1, {1.0, 5.0}, {5.0, 1.0}},
        {2, {0.0, 3.0}, {6.0, 3.0}}
    };
    int n_segs = sizeof(segs) / sizeof(segs[0]);

    printf("Кількість вхідних відрізків: %d\n", n_segs);

    Point pt;
    for (int i = 0; i < n_segs; ++i) {
        for (int j = i + 1; j < n_segs; ++j) {
            if (segments_intersect(segs[i], segs[j], &pt)) {
                printf("Знайдено перетин відрізків %d та %d у точці (%.2f, %.2f)\n",
                       segs[i].id, segs[j].id, pt.x, pt.y);
            }
        }
    }
    return 0;
}
