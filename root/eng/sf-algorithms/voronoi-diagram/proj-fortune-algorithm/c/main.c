#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define EPS 1e-9

typedef struct {
    double x;
    double y;
} Point;

typedef struct {
    Point start;
    Point end;
    Point direction;
    int site_left;
    int site_right;
    bool has_start;
    bool has_end;
} VoronoiEdge;

typedef enum { EVENT_SITE, EVENT_CIRCLE } EventType;

typedef struct Arc Arc;

typedef struct Event {
    double y;           /* Y-координата події для сортування в купі */
    Point point;        /* Координати сайта або центру кола */
    EventType type;
    Arc* arc;           /* Дуга, яка зникає (для коло-події) */
    bool valid;         /* Прапорець валідності події */
} Event;

struct Arc {
    Point site;
    int site_idx;
    Arc* prev;
    Arc* next;
    Event* circle_event;
    VoronoiEdge* edge_left;
    VoronoiEdge* edge_right;
};

/* Обчислення перетину двох парабол при поточному y_sweep */
static double get_breakpoint_x(Point p1, Point p2, double y_sweep) {
    if (fabs(p1.y - p2.y) < EPS) {
        return (p1.x + p2.x) / 2.0;
    }
    if (fabs(p1.y - y_sweep) < EPS) return p1.x;
    if (fabs(p2.y - y_sweep) < EPS) return p2.x;

    double d1 = 1.0 / (2.0 * (p1.y - y_sweep));
    double d2 = 1.0 / (2.0 * (p2.y - y_sweep));
    double a = d1 - d2;
    double b = 2.0 * (p2.x * d2 - p1.x * d1);
    double c = (p1.x * p1.x + p1.y * p1.y - y_sweep * y_sweep) * d1 -
               (p2.x * p2.x + p2.y * p2.y - y_sweep * y_sweep) * d2;

    double discr = b * b - 4.0 * a * c;
    if (discr < 0.0) discr = 0.0;
    double sq = sqrt(discr);

    double x1 = (-b + sq) / (2.0 * a);
    double x2 = (-b - sq) / (2.0 * a);

    return (p1.y < p2.y) ? fmax(x1, x2) : fmin(x1, x2);
}

/* Обчислення центру та радіуса описаного кола трьох точок */
static bool get_circumcenter(Point a, Point b, Point c, Point* center, double* bottom_y) {
    double d = 2.0 * (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y));
    if (d <= EPS) return false; /* Точки колінеарні або орієнтовані за стрілкою */

    double a2 = a.x * a.x + a.y * a.y;
    double b2 = b.x * b.x + b.y * b.y;
    double c2 = c.x * c.x + c.y * c.y;

    center->x = (a2 * (b.y - c.y) + b2 * (c.y - a.y) + c2 * (a.y - b.y)) / d;
    center->y = (a2 * (c.x - b.x) + b2 * (a.x - c.x) + c2 * (b.x - a.x)) / d;

    double r = hypot(center->x - a.x, center->y - a.y);
    *bottom_y = center->y - r;
    return true;
}

/* Черга подій: проста масивна реалізація пріоритетної черги */
typedef struct {
    Event* items[1024];
    int size;
} PriorityQueue;

static void pq_push(PriorityQueue* pq, Event* ev) {
    int i = pq->size++;
    while (i > 0) {
        int parent = (i - 1) / 2;
        if (pq->items[parent]->y >= ev->y) break;
        pq->items[i] = pq->items[parent];
        i = parent;
    }
    pq->items[i] = ev;
}

static Event* pq_pop(PriorityQueue* pq) {
    if (pq->size == 0) return NULL;
    Event* top = pq->items[0];
    Event* last = pq->items[--pq->size];
    if (pq->size > 0) {
        int i = 0;
        while (i * 2 + 1 < pq->size) {
            int left = i * 2 + 1;
            int right = i * 2 + 2;
            int best = left;
            if (right < pq->size && pq->items[right]->y > pq->items[left]->y) {
                best = right;
            }
            if (last->y >= pq->items[best]->y) break;
            pq->items[i] = pq->items[best];
            i = best;
        }
        pq->items[i] = last;
    }
    return top;
}

/* Динамічний масив вихідних ребер */
typedef struct {
    VoronoiEdge* data;
    int count;
    int capacity;
} EdgeList;

static VoronoiEdge* add_edge(EdgeList* list, int site1, int site2) {
    if (list->count >= list->capacity) {
        list->capacity = list->capacity == 0 ? 32 : list->capacity * 2;
        list->data = (VoronoiEdge*)realloc(list->data, list->capacity * sizeof(VoronoiEdge));
    }
    VoronoiEdge* e = &list->data[list->count++];
    e->site_left = site1;
    e->site_right = site2;
    e->has_start = false;
    e->has_end = false;
    return e;
}
