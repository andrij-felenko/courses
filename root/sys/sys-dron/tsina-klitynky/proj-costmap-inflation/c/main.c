#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define COST_FREE_SPACE          0
#define COST_INSCRIBED_OBSTACLE  253
#define COST_LETHAL_OBSTACLE     254
#define COST_NO_INFORMATION      255

#define MAX_QUEUE_SIZE           100000
#define MAX_PATH_LENGTH          2048

/* Конфігурація карти вартості */
typedef struct {
    uint32_t width;             /* Кількість клітинок по X */
    uint32_t height;            /* Кількість клітинок по Y */
    float resolution;           /* Розмір однієї клітинки (м) */
    float origin_x;             /* Світова координата X початку сітки */
    float origin_y;             /* Світова координата Y початку сітки */
    float inscribed_radius;     /* Вписаний радіус дрона (м) */
    float inflation_radius;     /* Зовнішній радіус інфляції (м) */
    float cost_scaling_factor;  /* Коефіцієнт альфа експоненційного спаду */
    float cost_weight;          /* Вага штрафу вартості для A* */
    float turn_penalty_weight;  /* Вага штрафу за зміну напрямку */
} CostmapConfig;

/* Структура карти вартості */
typedef struct {
    CostmapConfig config;
    uint8_t* cost_grid;         /* Підсумкова сітка вартостей */
    uint8_t* static_grid;       /* Шар статичних перешкод */
    uint8_t* lut;               /* Таблиця попередньо розрахованих вартостей */
    uint32_t lut_size;          /* Розмір таблиці LUT */
    int32_t cell_inflation_radius; /* Радіус інфляції в клітинках */
    int32_t cell_inscribed_radius; /* Вписаний радіус у клітинках */
} Costmap2D;

/* Елемент черги для багатоджерельного BFS інфляції */
typedef struct {
    int32_t x;
    int32_t y;
    int32_t src_x;
    int32_t src_y;
} InflationCell;

/* Проста кільцева черга для BFS */
typedef struct {
    InflationCell data[MAX_QUEUE_SIZE];
    uint32_t head;
    uint32_t tail;
    uint32_t count;
} BFSQueue;

static void queue_init(BFSQueue* q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
}

static bool queue_push(BFSQueue* q, InflationCell cell) {
    if (q->count >= MAX_QUEUE_SIZE) return false;
    q->data[q->tail] = cell;
    q->tail = (q->tail + 1) % MAX_QUEUE_SIZE;
    q->count++;
    return true;
}

static bool queue_pop(BFSQueue* q, InflationCell* cell) {
    if (q->count == 0) return false;
    *cell = q->data[q->head];
    q->head = (q->head + 1) % MAX_QUEUE_SIZE;
    q->count--;
    return true;
}

/* Ініціалізація та побудова таблиці LUT */
bool costmap_init(Costmap2D* map, CostmapConfig cfg) {
    map->config = cfg;
    uint32_t total_cells = cfg.width * cfg.height;

    map->cost_grid = (uint8_t*)malloc(total_cells);
    map->static_grid = (uint8_t*)malloc(total_cells);
    if (!map->cost_grid || !map->static_grid) return false;

    memset(map->cost_grid, COST_FREE_SPACE, total_cells);
    memset(map->static_grid, COST_FREE_SPACE, total_cells);

    map->cell_inflation_radius = (int32_t)ceilf(cfg.inflation_radius / cfg.resolution);
    map->cell_inscribed_radius = (int32_t)ceilf(cfg.inscribed_radius / cfg.resolution);

    /* Максимальна квадратична відстань у клітинках */
    uint32_t max_dist_sq = (uint32_t)(map->cell_inflation_radius * map->cell_inflation_radius) + 1;
    map->lut_size = max_dist_sq;
    map->lut = (uint8_t*)malloc(max_dist_sq);
    if (!map->lut) return false;

    /* Заповнення LUT експоненційним спадом */
    for (uint32_t d_sq = 0; d_sq < max_dist_sq; ++d_sq) {
        float dist_m = sqrtf((float)d_sq) * cfg.resolution;
        if (dist_m <= cfg.inscribed_radius) {
            map->lut[d_sq] = COST_INSCRIBED_OBSTACLE;
        } else if (dist_m >= cfg.inflation_radius) {
            map->lut[d_sq] = COST_FREE_SPACE;
        } else {
            float delta_d = dist_m - cfg.inscribed_radius;
            float factor = expf(-cfg.cost_scaling_factor * delta_d);
            float cost = factor * (float)(COST_INSCRIBED_OBSTACLE - 1);
            map->lut[d_sq] = (cost < 1.0f) ? COST_FREE_SPACE : (uint8_t)cost;
        }
    }

    return true;
}

void costmap_free(Costmap2D* map) {
    if (map->cost_grid) free(map->cost_grid);
    if (map->static_grid) free(map->static_grid);
    if (map->lut) free(map->lut);
    map->cost_grid = NULL;
    map->static_grid = NULL;
    map->lut = NULL;
}

/* Встановлення статичної перешкоди */
void costmap_set_obstacle(Costmap2D* map, uint32_t x, uint32_t y) {
    if (x < map->config.width && y < map->config.height) {
        map->static_grid[y * map->config.width + x] = COST_LETHAL_OBSTACLE;
    }
}

/* Швидка інфляція методом багатоджерельного BFS */
void costmap_update_inflation(Costmap2D* map) {
    uint32_t w = map->config.width;
    uint32_t h = map->config.height;
    uint32_t total_cells = w * h;

    /* Скопіювати статичну карту у підсумкову */
    memcpy(map->cost_grid, map->static_grid, total_cells);

    /* Масив відвіданих клітинок */
    bool* visited = (bool*)calloc(total_cells, sizeof(bool));
    if (!visited) return;

    BFSQueue queue;
    queue_init(&queue);

    /* 1. Пошук усіх летальних перешкод та ініціалізація черги */
    for (uint32_t y = 0; y < h; ++y) {
        for (uint32_t x = 0; x < w; ++x) {
            uint32_t idx = y * w + x;
            if (map->static_grid[idx] == COST_LETHAL_OBSTACLE) {
                InflationCell cell = {(int32_t)x, (int32_t)y, (int32_t)x, (int32_t)y};
                queue_push(&queue, cell);
                visited[idx] = true;
            }
        }
    }

    /* Зміщення 8 сусідів */
    const int32_t dx[8] = {-1, 1, 0, 0, -1, -1, 1, 1};
    const int32_t dy[8] = {0, 0, -1, 1, -1, 1, -1, 1};

    /* 2. Поширення хвилі інфляції */
    InflationCell current;
    while (queue_pop(&queue, &current)) {
        for (int i = 0; i < 8; ++i) {
            int32_t nx = current.x + dx[i];
            int32_t ny = current.y + dy[i];

            if (nx < 0 || nx >= (int32_t)w || ny < 0 || ny >= (int32_t)h) continue;

            uint32_t n_idx = (uint32_t)(ny * w + nx);
            if (visited[n_idx]) continue;

            /* Квадрат відстані до первинного джерела перешкоди */
            int32_t diff_x = nx - current.src_x;
            int32_t diff_y = ny - current.src_y;
            uint32_t dist_sq = (uint32_t)(diff_x * diff_x + diff_y * diff_y);

            if (dist_sq >= map->lut_size) continue;

            uint8_t cost = map->lut[dist_sq];
            if (cost > COST_FREE_SPACE) {
                if (map->cost_grid[n_idx] < cost) {
                    map->cost_grid[n_idx] = cost;
                }
                visited[n_idx] = true;
                InflationCell next_cell = {nx, ny, current.src_x, current.src_y};
                queue_push(&queue, next_cell);
            }
        }
    }

    free(visited);
}

/* =========================================================================
 * Планувальник траєкторії A* на карті вартості
 * ========================================================================= */

typedef struct {
    int32_t x;
    int32_t y;
    float g_cost;
    float f_cost;
    int32_t parent_idx;
} AStarNode;

typedef struct {
    AStarNode nodes[MAX_QUEUE_SIZE];
    uint32_t size;
} PriorityQueue;

static void pq_init(PriorityQueue* pq) {
    pq->size = 0;
}

static void pq_push(PriorityQueue* pq, AStarNode node) {
    if (pq->size >= MAX_QUEUE_SIZE) return;
    uint32_t i = pq->size++;
    while (i > 0) {
        uint32_t parent = (i - 1) / 2;
        if (pq->nodes[parent].f_cost <= node.f_cost) break;
        pq->nodes[i] = pq->nodes[parent];
        i = parent;
    }
    pq->nodes[i] = node;
}

static bool pq_pop(PriorityQueue* pq, AStarNode* min_node) {
    if (pq->size == 0) return false;
    *min_node = pq->nodes[0];
    AStarNode last = pq->nodes[--pq->size];
    if (pq->size == 0) return true;

    uint32_t i = 0;
    while (i * 2 + 1 < pq->size) {
        uint32_t left = i * 2 + 1;
        uint32_t right = i * 2 + 2;
        uint32_t smallest = left;
        if (right < pq->size && pq->nodes[right].f_cost < pq->nodes[left].f_cost) {
            smallest = right;
        }
        if (last.f_cost <= pq->nodes[smallest].f_cost) break;
        pq->nodes[i] = pq->nodes[smallest];
        i = smallest;
    }
    pq->nodes[i] = last;
    return true;
}

/* Точка траєкторії */
typedef struct {
    int32_t x;
    int32_t y;
} PathPoint;

/* Пошук шляху A* */
int32_t astar_plan(const Costmap2D* map,
                   int32_t start_x, int32_t start_y,
                   int32_t goal_x, int32_t goal_y,
                   PathPoint* out_path, int32_t max_path_len) {
    uint32_t w = map->config.width;
    uint32_t h = map->config.height;
    uint32_t total_cells = w * h;

    if (start_x < 0 || start_x >= (int32_t)w || start_y < 0 || start_y >= (int32_t)h) return -1;
    if (goal_x < 0 || goal_x >= (int32_t)w || goal_y < 0 || goal_y >= (int32_t)h) return -1;

    /* Якщо старт або ціль у зоні інфляції/перешкоди */
    if (map->cost_grid[start_y * w + start_x] >= COST_INSCRIBED_OBSTACLE) return -1;
    if (map->cost_grid[goal_y * w + goal_x] >= COST_INSCRIBED_OBSTACLE) return -1;

    float* g_score = (float*)malloc(total_cells * sizeof(float));
    int32_t* parent_map = (int32_t*)malloc(total_cells * sizeof(int32_t));
    bool* closed = (bool*)calloc(total_cells, sizeof(bool));
    if (!g_score || !parent_map || !closed) {
        if (g_score) free(g_score);
        if (parent_map) free(parent_map);
        if (closed) free(closed);
        return -1;
    }

    for (uint32_t i = 0; i < total_cells; ++i) {
        g_score[i] = INFINITY;
        parent_map[i] = -1;
    }

    PriorityQueue pq;
    pq_init(&pq);

    uint32_t start_idx = start_y * w + start_x;
    g_score[start_idx] = 0.0f;

    float h_start = hypotf((float)(goal_x - start_x), (float)(goal_y - start_y)) * map->config.resolution;
    AStarNode start_node = {start_x, start_y, 0.0f, h_start, -1};
    pq_push(&pq, start_node);

    const int32_t dx[8] = {-1, 1, 0, 0, -1, -1, 1, 1};
    const int32_t dy[8] = {0, 0, -1, 1, -1, 1, -1, 1};
    const float step_base[8] = {1.0f, 1.0f, 1.0f, 1.0f, 1.41421356f, 1.41421356f, 1.41421356f, 1.41421356f};

    bool found = false;
    uint32_t goal_idx = goal_y * w + goal_x;

    AStarNode current;
    while (pq_pop(&pq, &current)) {
        uint32_t curr_idx = current.y * w + current.x;
        if (closed[curr_idx]) continue;
        closed[curr_idx] = true;

        if (current.x == goal_x && current.y == goal_y) {
            found = true;
            break;
        }

        for (int i = 0; i < 8; ++i) {
            int32_t nx = current.x + dx[i];
            int32_t ny = current.y + dy[i];

            if (nx < 0 || nx >= (int32_t)w || ny < 0 || ny >= (int32_t)h) continue;

            uint32_t n_idx = ny * w + nx;
            if (closed[n_idx]) continue;

            uint8_t cell_cost = map->cost_grid[n_idx];
            if (cell_cost >= COST_INSCRIBED_OBSTACLE) continue;

            /* Розрахунок вартості переходу */
            float cost_factor = 1.0f + map->config.cost_weight * ((float)cell_cost / 254.0f);
            float edge_cost = step_base[i] * map->config.resolution * cost_factor;

            /* Кінематичний штраф за зміну напрямку */
            float turn_penalty = 0.0f;
            if (current.parent_idx >= 0) {
                int32_t px = current.parent_idx % w;
                int32_t py = current.parent_idx / w;
                int32_t dir1_x = current.x - px;
                int32_t dir1_y = current.y - py;
                int32_t dir2_x = dx[i];
                int32_t dir2_y = dy[i];

                float dot = (float)(dir1_x * dir2_x + dir1_y * dir2_y);
                float len1 = sqrtf((float)(dir1_x * dir1_x + dir1_y * dir1_y));
                float len2 = sqrtf((float)(dir2_x * dir2_x + dir2_y * dir2_y));
                if (len1 > 0.0f && len2 > 0.0f) {
                    float cos_theta = dot / (len1 * len2);
                    if (cos_theta > 1.0f) cos_theta = 1.0f;
                    if (cos_theta < -1.0f) cos_theta = -1.0f;
                    turn_penalty = map->config.turn_penalty_weight * (1.0f - cos_theta);
                }
            }

            float tentative_g = current.g_cost + edge_cost + turn_penalty;
            if (tentative_g < g_score[n_idx]) {
                g_score[n_idx] = tentative_g;
                parent_map[n_idx] = (int32_t)curr_idx;

                float h = hypotf((float)(goal_x - nx), (float)(goal_y - ny)) * map->config.resolution;
                AStarNode neighbor = {nx, ny, tentative_g, tentative_g + h, (int32_t)curr_idx};
                pq_push(&pq, neighbor);
            }
        }
    }

    int32_t path_len = 0;
    if (found) {
        int32_t curr = (int32_t)goal_idx;
        while (curr >= 0 && path_len < max_path_len) {
            out_path[path_len].x = curr % w;
            out_path[path_len].y = curr / w;
            path_len++;
            if (curr == (int32_t)start_idx) break;
            curr = parent_map[curr];
        }

        /* Розвернути масив шляху від старту до фінішу */
        for (int32_t i = 0; i < path_len / 2; ++i) {
            PathPoint temp = out_path[i];
            out_path[i] = out_path[path_len - 1 - i];
            out_path[path_len - 1 - i] = temp;
        }
    }

    free(g_score);
    free(parent_map);
    free(closed);

    return found ? path_len : -1;
}

int main(void) {
    CostmapConfig cfg = {
        .width = 40,
        .height = 40,
        .resolution = 0.5f,
        .origin_x = 0.0f,
        .origin_y = 0.0f,
        .inscribed_radius = 0.6f,
        .inflation_radius = 2.0f,
        .cost_scaling_factor = 2.5f,
        .cost_weight = 4.0f,
        .turn_penalty_weight = 0.5f
    };

    Costmap2D map;
    if (!costmap_init(&map, cfg)) {
        printf("Помилка ініціалізації карти!\n");
        return 1;
    }

    /* Створення L-подібної стіни */
    for (int y = 10; y <= 25; ++y) costmap_set_obstacle(&map, 15, y);
    for (int x = 15; x <= 25; ++x) costmap_set_obstacle(&map, x, 25);

    /* Запуск швидкої інфляції */
    costmap_update_inflation(&map);

    /* Пошук траєкторії */
    PathPoint path[MAX_PATH_LENGTH];
    int32_t len = astar_plan(&map, 5, 5, 30, 30, path, MAX_PATH_LENGTH);

    printf("Результат планування A* на карті вартості:\n");
    if (len > 0) {
        printf("Шлях знайдено! Кількість точок: %d\n", len);
        printf("Старт: (%d, %d) -> Фініш: (%d, %d)\n", path[0].x, path[0].y, path[len-1].x, path[len-1].y);
    } else {
        printf("Шлях не знайдено (перешкода блокує прохід)!\n");
    }

    costmap_free(&map);
    return 0;
}
