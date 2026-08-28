#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define GRID_DIM 128
#define GRID_MASK (GRID_DIM - 1)
#define GRID_RESOLUTION 0.1f /* 10 см на комірку */

#define LOG_ODDS_FREE -62   /* -0.62 * 100 */
#define LOG_ODDS_OCC   173  /* +1.73 * 100 */
#define LOG_ODDS_MIN  -400  /* -4.00 * 100 */
#define LOG_ODDS_MAX   400  /* +4.00 * 100 */
#define LOG_ODDS_OCC_THRESH 100

#define NUM_SECTORS 72
#define SECTOR_ANGLE_DEG 5.0f
#define DEG_TO_RAD(d) ((d) * 0.017453292519943295f)
#define RAD_TO_DEG(r) ((r) * 57.29577951308232f)

typedef enum {
    TACTIC_ACTION_PROCEED = 0,
    TACTIC_ACTION_BRAKE,
    TACTIC_ACTION_BYPASS_LEFT,
    TACTIC_ACTION_BYPASS_RIGHT,
    TACTIC_ACTION_CLIMB
} AvoidanceAction;

typedef struct {
    AvoidanceAction action;
    float target_heading_rad;
    float recommended_speed_mps;
} AvoidanceOutput;

typedef struct {
    int16_t log_odds[GRID_DIM][GRID_DIM];
    uint8_t cost_layer[GRID_DIM][GRID_DIM];
    float origin_world_x;
    float origin_world_y;
    int32_t grid_offset_x;
    int32_t grid_offset_y;
} LocalOccupancyGridC;

static inline float normalize_angle(float a) {
    while (a > 3.14159265f) a -= 6.28318530f;
    while (a < -3.14159265f) a += 6.28318530f;
    return a;
}

void local_grid_init(LocalOccupancyGridC *grid, float init_x, float init_y) {
    memset(grid->log_odds, 0, sizeof(grid->log_odds));
    memset(grid->cost_layer, 0, sizeof(grid->cost_layer));
    grid->origin_world_x = init_x;
    grid->origin_world_y = init_y;
    grid->grid_offset_x = 0;
    grid->grid_offset_y = 0;
}

void local_grid_shift_origin(LocalOccupancyGridC *grid, float new_x, float new_y) {
    float dx = new_x - grid->origin_world_x;
    float dy = new_y - grid->origin_world_y;

    int32_t shift_cells_x = (int32_t)(dx / GRID_RESOLUTION);
    int32_t shift_cells_y = (int32_t)(dy / GRID_RESOLUTION);

    if (shift_cells_x == 0 && shift_cells_y == 0) return;

    if (abs(shift_cells_x) >= GRID_DIM || abs(shift_cells_y) >= GRID_DIM) {
        local_grid_init(grid, new_x, new_y);
        return;
    }

    if (shift_cells_x > 0) {
        for (int32_t x = 0; x < shift_cells_x; ++x) {
            int32_t col = (grid->grid_offset_x + x) & GRID_MASK;
            for (int32_t y = 0; y < GRID_DIM; ++y) {
                grid->log_odds[col][y] = 0;
                grid->cost_layer[col][y] = 0;
            }
        }
    } else if (shift_cells_x < 0) {
        for (int32_t x = shift_cells_x; x < 0; ++x) {
            int32_t col = (grid->grid_offset_x + GRID_DIM + x) & GRID_MASK;
            for (int32_t y = 0; y < GRID_DIM; ++y) {
                grid->log_odds[col][y] = 0;
                grid->cost_layer[col][y] = 0;
            }
        }
    }

    if (shift_cells_y > 0) {
        for (int32_t y = 0; y < shift_cells_y; ++y) {
            int32_t row = (grid->grid_offset_y + y) & GRID_MASK;
            for (int32_t x = 0; x < GRID_DIM; ++x) {
                grid->log_odds[x][row] = 0;
                grid->cost_layer[x][row] = 0;
            }
        }
    } else if (shift_cells_y < 0) {
        for (int32_t y = shift_cells_y; y < 0; ++y) {
            int32_t row = (grid->grid_offset_y + GRID_DIM + y) & GRID_MASK;
            for (int32_t x = 0; x < GRID_DIM; ++x) {
                grid->log_odds[x][row] = 0;
                grid->cost_layer[x][row] = 0;
            }
        }
    }

    grid->grid_offset_x = (grid->grid_offset_x + shift_cells_x) & GRID_MASK;
    grid->grid_offset_y = (grid->grid_offset_y + shift_cells_y) & GRID_MASK;
    grid->origin_world_x += (float)shift_cells_x * GRID_RESOLUTION;
    grid->origin_world_y += (float)shift_cells_y * GRID_RESOLUTION;
}

static inline bool local_grid_world_to_indices(const LocalOccupancyGridC *grid, float wx, float wy, int32_t *ix, int32_t *iy) {
    float lx = wx - (grid->origin_world_x - ((float)GRID_DIM * GRID_RESOLUTION * 0.5f));
    float ly = wy - (grid->origin_world_y - ((float)GRID_DIM * GRID_RESOLUTION * 0.5f));

    int32_t cx = (int32_t)(lx / GRID_RESOLUTION);
    int32_t cy = (int32_t)(ly / GRID_RESOLUTION);

    if (cx < 0 || cx >= GRID_DIM || cy < 0 || cy >= GRID_DIM) {
        return false;
    }

    *ix = (grid->grid_offset_x + cx) & GRID_MASK;
    *iy = (grid->grid_offset_y + cy) & GRID_MASK;
    return true;
}

static inline void local_grid_update_cell_log_odds(LocalOccupancyGridC *grid, int32_t ix, int32_t iy, int16_t delta) {
    int32_t nv = (int32_t)grid->log_odds[ix][iy] + delta;
    if (nv < LOG_ODDS_MIN) nv = LOG_ODDS_MIN;
    if (nv > LOG_ODDS_MAX) nv = LOG_ODDS_MAX;
    grid->log_odds[ix][iy] = (int16_t)nv;

    if (grid->log_odds[ix][iy] >= LOG_ODDS_OCC_THRESH) {
        grid->cost_layer[ix][iy] = 255;
    } else if (grid->log_odds[ix][iy] <= LOG_ODDS_FREE) {
        grid->cost_layer[ix][iy] = 0;
    }
}

void local_grid_update_ray(LocalOccupancyGridC *grid, float start_x, float start_y, float end_x, float end_y, bool hit) {
    int32_t x0, y0, x1, y1;
    if (!local_grid_world_to_indices(grid, start_x, start_y, &x0, &y0)) return;
    if (!local_grid_world_to_indices(grid, end_x, end_y, &x1, &y1)) return;

    int32_t dx = abs(x1 - x0);
    int32_t dy = abs(y1 - y0);
    int32_t sx = (x0 < x1) ? 1 : -1;
    int32_t sy = (y0 < y1) ? 1 : -1;
    int32_t err = dx - dy;

    int32_t cx = x0;
    int32_t cy = y0;

    while (cx != x1 || cy != y1) {
        local_grid_update_cell_log_odds(grid, cx, cy, LOG_ODDS_FREE);
        int32_t e2 = 2 * err;
        if (e2 > -dy) {
            err -= dy;
            cx = (cx + sx) & GRID_MASK;
        }
        if (e2 < dx) {
            err += dx;
            cy = (cy + sy) & GRID_MASK;
        }
    }

    if (hit) {
        local_grid_update_cell_log_odds(grid, x1, y1, LOG_ODDS_OCC);
    }
}

void local_grid_inflate_obstacles(LocalOccupancyGridC *grid, float safety_radius_m) {
    int32_t rad_cells = (int32_t)(safety_radius_m / GRID_RESOLUTION);
    if (rad_cells <= 0) return;

    for (int32_t x = 0; x < GRID_DIM; ++x) {
        for (int32_t y = 0; y < GRID_DIM; ++y) {
            if (grid->log_odds[x][y] >= LOG_ODDS_OCC_THRESH) {
                for (int32_t dx = -rad_cells; dx <= rad_cells; ++dx) {
                    for (int32_t dy = -rad_cells; dy <= rad_cells; ++dy) {
                        if (dx * dx + dy * dy <= rad_cells * rad_cells) {
                            int32_t nx = (x + dx) & GRID_MASK;
                            int32_t ny = (y + dy) & GRID_MASK;
                            if (grid->cost_layer[nx][ny] < 200) {
                                grid->cost_layer[nx][ny] = 200;
                            }
                        }
                    }
                }
            }
        }
    }
}

AvoidanceOutput local_grid_compute_vfh_tactic(
    const LocalOccupancyGridC *grid,
    float current_speed_mps,
    float target_heading_rad,
    float current_heading_rad,
    float max_braking_accel
) {
    AvoidanceOutput out;
    out.action = TACTIC_ACTION_PROCEED;
    out.target_heading_rad = target_heading_rad;
    out.recommended_speed_mps = current_speed_mps;

    float stop_dist = (current_speed_mps * current_speed_mps) / (2.0f * max_braking_accel) + current_speed_mps * 0.2f + 0.8f;
    int32_t max_scan_cells = (int32_t)(stop_dist / GRID_RESOLUTION);
    if (max_scan_cells > (GRID_DIM / 2 - 2)) max_scan_cells = (GRID_DIM / 2 - 2);

    float polar_density[NUM_SECTORS];
    memset(polar_density, 0, sizeof(polar_density));

    int32_t center_x = grid->grid_offset_x + (GRID_DIM / 2);
    int32_t center_y = grid->grid_offset_y + (GRID_DIM / 2);

    for (int32_t dx = -max_scan_cells; dx <= max_scan_cells; ++dx) {
        for (int32_t dy = -max_scan_cells; dy <= max_scan_cells; ++dy) {
            float dist_sq = (float)(dx * dx + dy * dy);
            if (dist_sq <= 1.0f || dist_sq > (float)(max_scan_cells * max_scan_cells)) continue;

            int32_t cx = (center_x + dx) & GRID_MASK;
            int32_t cy = (center_y + dy) & GRID_MASK;

            uint8_t cost = grid->cost_layer[cx][cy];
            if (cost > 0) {
                float dist = sqrtf(dist_sq);
                float angle = atan2f((float)dy, (float)dx);
                float rel_angle = normalize_angle(angle - current_heading_rad);
                float deg = RAD_TO_DEG(rel_angle);
                if (deg < 0.0f) deg += 360.0f;

                int32_t sector = (int32_t)(deg / SECTOR_ANGLE_DEG) % NUM_SECTORS;
                float weight = ((float)cost / 255.0f) * ((float)max_scan_cells - dist) / (float)max_scan_cells;
                polar_density[sector] += weight;
            }
        }
    }

    int32_t fwd_sector = 0;
    float front_threat = polar_density[fwd_sector] + polar_density[(fwd_sector + 1) % NUM_SECTORS] + polar_density[(fwd_sector + NUM_SECTORS - 1) % NUM_SECTORS];

    if (front_threat < 0.3f) {
        out.action = TACTIC_ACTION_PROCEED;
        out.target_heading_rad = target_heading_rad;
        return out;
    }

    if (front_threat > 2.5f && current_speed_mps > 1.5f) {
        out.action = TACTIC_ACTION_BRAKE;
        out.recommended_speed_mps = 0.0f;
        return out;
    }

    float best_cost = 1e9f;
    int32_t best_sector = -1;
    float target_rel_angle = normalize_angle(target_heading_rad - current_heading_rad);
    float target_deg = RAD_TO_DEG(target_rel_angle);
    if (target_deg < 0.0f) target_deg += 360.0f;

    for (int32_t s = 0; s < NUM_SECTORS; ++s) {
        if (polar_density[s] < 0.5f) {
            float s_angle_rad = DEG_TO_RAD((float)s * SECTOR_ANGLE_DEG);
            if (s_angle_rad > 3.14159265f) s_angle_rad -= 6.28318530f;

            float diff_target = fabsf(normalize_angle(s_angle_rad - target_rel_angle));
            float diff_current = fabsf(normalize_angle(s_angle_rad));
            float cost = 2.0f * diff_target + 1.0f * diff_current + polar_density[s] * 3.0f;

            if (cost < best_cost) {
                best_cost = cost;
                best_sector = s;
            }
        }
    }

    if (best_sector != -1) {
        float chosen_rel_rad = DEG_TO_RAD((float)best_sector * SECTOR_ANGLE_DEG);
        if (chosen_rel_rad > 3.14159265f) chosen_rel_rad -= 6.28318530f;
        out.target_heading_rad = normalize_angle(current_heading_rad + chosen_rel_rad);
        out.action = (chosen_rel_rad < 0.0f) ? TACTIC_ACTION_BYPASS_LEFT : TACTIC_ACTION_BYPASS_RIGHT;
        out.recommended_speed_mps = current_speed_mps * 0.75f;
    } else {
        out.action = TACTIC_ACTION_CLIMB;
        out.recommended_speed_mps = current_speed_mps * 0.3f;
    }

    return out;
}
