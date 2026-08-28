#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <stdlib.h>

#define GRID_SIZE_X 100
#define GRID_SIZE_Y 100
#define GRID_RES    0.1f

#define L_FREE -62   /* -0.62 * 100 у фіксованій крапці */
#define L_OCC   173  /* +1.73 * 100 */
#define L_MIN  -400  /* -4.00 * 100 */
#define L_MAX   400  /* +4.00 * 100 */
#define L_OCC_THRESHOLD 100

typedef enum {
    TACTIC_PROCEED,
    TACTIC_BRAKE,
    TACTIC_BYPASS_LEFT,
    TACTIC_BYPASS_RIGHT,
    TACTIC_CLIMB
} AvoidanceTactic;

typedef struct {
    int16_t cells[GRID_SIZE_X][GRID_SIZE_Y];
    float origin_x;
    float origin_y;
} OccupancyGrid2D;

void grid_init(OccupancyGrid2D *grid, float start_x, float start_y) {
    grid->origin_x = start_x;
    grid->origin_y = start_y;
    for (int x = 0; x < GRID_SIZE_X; ++x) {
        for (int y = 0; y < GRID_SIZE_Y; ++y) {
            grid->cells[x][y] = 0;
        }
    }
}

static inline bool world_to_grid(const OccupancyGrid2D *grid, float wx, float wy, int *gx, int *gy) {
    float local_x = wx - (grid->origin_x - (GRID_SIZE_X * GRID_RES * 0.5f));
    float local_y = wy - (grid->origin_y - (GRID_SIZE_Y * GRID_RES * 0.5f));
    
    int x = (int)(local_x / GRID_RES);
    int y = (int)(local_y / GRID_RES);
    
    if (x < 0 || x >= GRID_SIZE_X || y < 0 || y >= GRID_SIZE_Y) {
        return false;
    }
    *gx = x;
    *gy = y;
    return true;
}

static inline void update_cell(OccupancyGrid2D *grid, int gx, int gy, int16_t delta_l) {
    int32_t val = (int32_t)grid->cells[gx][gy] + delta_l;
    if (val < L_MIN) val = L_MIN;
    if (val > L_MAX) val = L_MAX;
    grid->cells[gx][gy] = (int16_t)val;
}

void grid_update_ray(OccupancyGrid2D *grid, float sx, float sy, float hx, float hy, bool hit_detected) {
    int x0, y0, x1, y1;
    if (!world_to_grid(grid, sx, sy, &x0, &y0)) return;
    if (!world_to_grid(grid, hx, hy, &x1, &y1)) return;

    int dx = abs(x1 - x0);
    int dy = abs(y1 - y0);
    int step_x = (x0 < x1) ? 1 : -1;
    int step_y = (y0 < y1) ? 1 : -1;
    int err = dx - dy;
    
    int curr_x = x0;
    int curr_y = y0;

    while (curr_x != x1 || curr_y != y1) {
        update_cell(grid, curr_x, curr_y, L_FREE);
        int e2 = 2 * err;
        if (e2 > -dy) {
            err -= dy;
            curr_x += step_x;
        }
        if (e2 < dx) {
            err += dx;
            curr_y += step_y;
        }
    }

    if (hit_detected) {
        update_cell(grid, x1, y1, L_OCC);
    }
}

AvoidanceTactic evaluate_avoidance(const OccupancyGrid2D *grid, float speed, float max_decel, float *out_angle) {
    int cx = GRID_SIZE_X / 2;
    int cy = GRID_SIZE_Y / 2;
    
    float d_stop = (speed * speed) / (2.0f * max_decel) + speed * 0.15f + 0.8f;
    int check_cells = (int)(d_stop / GRID_RES);

    int front_blocked_dist = 0;
    for (int step = 1; step <= check_cells && (cx + step) < GRID_SIZE_X; ++step) {
        if (grid->cells[cx + step][cy] >= L_OCC_THRESHOLD) {
            front_blocked_dist = step;
            break;
        }
    }

    if (front_blocked_dist == 0) {
        *out_angle = 0.0f;
        return TACTIC_PROCEED;
    }

    if (front_blocked_dist <= (int)(1.2f / GRID_RES)) {
        return TACTIC_BRAKE;
    }

    int left_free = 0;
    int right_free = 0;
    for (int step = 1; step <= check_cells; ++step) {
        if (cy - step >= 0 && grid->cells[cx + step][cy - step] < L_OCC_THRESHOLD) {
            left_free++;
        }
        if (cy + step < GRID_SIZE_Y && grid->cells[cx + step][cy + step] < L_OCC_THRESHOLD) {
            right_free++;
        }
    }

    if (left_free > right_free && left_free > 5) {
        *out_angle = -0.5235f; /* -30 градусів */
        return TACTIC_BYPASS_LEFT;
    } else if (right_free >= left_free && right_free > 5) {
        *out_angle = 0.5235f;  /* +30 градусів */
        return TACTIC_BYPASS_RIGHT;
    }

    return TACTIC_CLIMB;
}
