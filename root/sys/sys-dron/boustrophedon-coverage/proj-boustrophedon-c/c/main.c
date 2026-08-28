#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define MAX_VERTICES 256
#define MAX_CELLS 64
#define MAX_WAYPOINTS 2048
#define EPSILON 1e-6

typedef enum {
    EVENT_IN,
    EVENT_OUT,
    EVENT_SPLIT,
    EVENT_MERGE,
    EVENT_REGULAR
} EventType;

typedef struct {
    double x;
    double y;
} Point2D;

typedef struct {
    Point2D p1;
    Point2D p2;
    bool is_obstacle;
} Edge2D;

typedef struct {
    Point2D pt;
    EventType type;
    int poly_idx;
    int vert_idx;
} SweepEvent;

typedef struct {
    int id;
    double x_min;
    double x_max;
    Point2D waypoints[MAX_WAYPOINTS];
    int waypoint_count;
    int neighbors[MAX_CELLS];
    int neighbor_count;
    bool visited;
} BcdCell;

typedef struct {
    BcdCell cells[MAX_CELLS];
    int cell_count;
} BcdDecomposition;

/* Порівняння для впорядкування подій замітання */
static int compare_events(const void *a, const void *b) {
    const SweepEvent *ea = (const SweepEvent *)a;
    const SweepEvent *eb = (const SweepEvent *)b;
    if (fabs(ea->pt.x - eb->pt.x) > EPSILON) {
        return (ea->pt.x < eb->pt.x) ? -1 : 1;
    }
    if (fabs(ea->pt.y - eb->pt.y) > EPSILON) {
        return (ea->pt.y < eb->pt.y) ? -1 : 1;
    }
    return 0;
}

/* Визначення типу критичної точки за суміжними ребрами */
static EventType classify_vertex(Point2D prev, Point2D curr, Point2D next, bool is_obstacle) {
    double dx1 = prev.x - curr.x;
    double dx2 = next.x - curr.x;

    if (dx1 > EPSILON && dx2 > EPSILON) {
        /* Обидва ребра праворуч */
        return is_obstacle ? EVENT_SPLIT : EVENT_IN;
    }
    if (dx1 < -EPSILON && dx2 < -EPSILON) {
        /* Обидва ребра ліворуч */
        return is_obstacle ? EVENT_MERGE : EVENT_OUT;
    }
    return EVENT_REGULAR;
}

/* Генерація паралельних галсів усередині однієї монотонної комірки */
static void generate_cell_stripes(BcdCell *cell, double top_y, double bot_y, double step_d) {
    cell->waypoint_count = 0;
    double cur_x = cell->x_min + step_d * 0.5;
    bool moving_up = true;

    while (cur_x <= cell->x_max + EPSILON && cell->waypoint_count + 2 < MAX_WAYPOINTS) {
        if (moving_up) {
            cell->waypoints[cell->waypoint_count++] = (Point2D){ cur_x, bot_y };
            cell->waypoints[cell->waypoint_count++] = (Point2D){ cur_x, top_y };
        } else {
            cell->waypoints[cell->waypoint_count++] = (Point2D){ cur_x, top_y };
            cell->waypoints[cell->waypoint_count++] = (Point2D){ cur_x, bot_y };
        }
        moving_up = !moving_up;
        cur_x += step_d;
    }
}

/* Ініціалізація розкладу */
void bcd_init(BcdDecomposition *bcd) {
    bcd->cell_count = 0;
    for (int i = 0; i < MAX_CELLS; ++i) {
        bcd->cells[i].id = i;
        bcd->cells[i].waypoint_count = 0;
        bcd->cells[i].neighbor_count = 0;
        bcd->cells[i].visited = false;
    }
}

/* Створення тестового середовища з перешкодою */
void build_demo_environment(Point2D *outer, int *n_outer, Point2D *obs, int *n_obs) {
    *n_outer = 4;
    outer[0] = (Point2D){ 0.0, 0.0 };
    outer[1] = (Point2D){ 100.0, 0.0 };
    outer[2] = (Point2D){ 100.0, 60.0 };
    outer[3] = (Point2D){ 0.0, 60.0 };

    *n_obs = 4;
    obs[0] = (Point2D){ 35.0, 30.0 };
    obs[1] = (Point2D){ 55.0, 15.0 };
    obs[2] = (Point2D){ 65.0, 30.0 };
    obs[3] = (Point2D){ 55.0, 45.0 };
}

/* Виконання обходу в глибину (DFS) для зшивання маршруту */
void plan_global_tour(BcdDecomposition *bcd, int current_cell, Point2D *global_path, int *path_len) {
    bcd->cells[current_cell].visited = true;
    BcdCell *c = &bcd->cells[current_cell];

    /* Додаємо всі галси поточної комірки */
    for (int i = 0; i < c->waypoint_count && *path_len < MAX_WAYPOINTS; ++i) {
        global_path[(*path_len)++] = c->waypoints[i];
    }

    /* Рекурсивно переходимо до невідвіданих сусідів */
    for (int i = 0; i < c->neighbor_count; ++i) {
        int nxt = c->neighbors[i];
        if (!bcd->cells[nxt].visited) {
            plan_global_tour(bcd, nxt, global_path, path_len);
        }
    }
}

int main(void) {
    Point2D outer[MAX_VERTICES], obs[MAX_VERTICES];
    int n_outer = 0, n_obs = 0;
    build_demo_environment(outer, &n_outer, obs, &n_obs);

    BcdDecomposition bcd;
    bcd_init(&bcd);

    /* Демонстраційний розклад на 4 комірки навколо перешкоди */
    double step_d = 5.0;

    /* Комірка 1: ліва зона перед перешкодою (0..35) */
    BcdCell *c1 = &bcd.cells[bcd.cell_count++];
    c1->x_min = 0.0; c1->x_max = 35.0;
    generate_cell_stripes(c1, 60.0, 0.0, step_d);

    /* Комірка 2: верхній коридор (35..65) */
    BcdCell *c2 = &bcd.cells[bcd.cell_count++];
    c2->x_min = 35.0; c2->x_max = 65.0;
    generate_cell_stripes(c2, 60.0, 45.0, step_d);

    /* Комірка 3: нижній коридор (35..65) */
    BcdCell *c3 = &bcd.cells[bcd.cell_count++];
    c3->x_min = 35.0; c3->x_max = 65.0;
    generate_cell_stripes(c3, 15.0, 0.0, step_d);

    /* Комірка 4: права зона за перешкодою (65..100) */
    BcdCell *c4 = &bcd.cells[bcd.cell_count++];
    c4->x_min = 65.0; c4->x_max = 100.0;
    generate_cell_stripes(c4, 60.0, 0.0, step_d);

    /* Встановлення суміжності в графі */
    c1->neighbors[c1->neighbor_count++] = 1;
    c1->neighbors[c1->neighbor_count++] = 2;

    c2->neighbors[c2->neighbor_count++] = 0;
    c2->neighbors[c2->neighbor_count++] = 3;

    c3->neighbors[c3->neighbor_count++] = 0;
    c3->neighbors[c3->neighbor_count++] = 3;

    c4->neighbors[c4->neighbor_count++] = 1;
    c4->neighbors[c4->neighbor_count++] = 2;

    Point2D global_path[MAX_WAYPOINTS];
    int path_len = 0;
    plan_global_tour(&bcd, 0, global_path, &path_len);

    printf("Побудовано бустрофедонний розклад: %d комірок, сумарно %d точок маршруту\n",
           bcd.cell_count, path_len);

    return 0;
}
