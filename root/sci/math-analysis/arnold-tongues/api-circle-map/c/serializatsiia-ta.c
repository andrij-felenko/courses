#include <stddef.h>
#include <stdint.h>

typedef struct {
    double current_x;
    int64_t total_turns;
    double omega;
    double k;
    size_t current_step;
} circle_map_state_t;

/**
 * @brief Зберігає поточний стан траєкторії у структуру стану.
 */
circle_map_status_t circle_map_save_state(
    double x, int64_t turns, double omega, double k, size_t step,
    circle_map_state_t *out_state
);
