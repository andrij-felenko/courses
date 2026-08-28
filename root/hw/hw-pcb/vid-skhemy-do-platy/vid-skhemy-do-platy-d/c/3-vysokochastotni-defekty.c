#include <stdio.h>
#include <math.h>

typedef struct {
    double x_min;
    double y_min;
    double x_max;
    double y_max;
    int net_id;
    char label[32];
} CopperPrimitive;

double primitive_distance(const CopperPrimitive* a, const CopperPrimitive* b) {
    double dx = 0.0;
    if (a->x_max < b->x_min) {
        dx = b->x_min - a->x_max;
    } else if (b->x_max < a->x_min) {
        dx = a->x_min - b->x_max;
    }

    double dy = 0.0;
    if (a->y_max < b->y_min) {
        dy = b->y_min - a->y_max;
    } else if (b->y_max < a->y_min) {
        dy = a->y_min - b->y_max;
    }

    return sqrt(dx * dx + dy * dy);
}

int evaluate_clearance_drc(const CopperPrimitive* a, const CopperPrimitive* b,
                           double required_clearance, char* log_buffer, size_t log_size) {
    if (!a || !b) return 0;
    if (a->net_id == b->net_id) return 1; // Один ланцюг — зазор дозволено

    double actual_dist = primitive_distance(a, b);
    if (actual_dist < required_clearance) {
        if (log_buffer && log_size > 0) {
            snprintf(log_buffer, log_size,
                     "DRC VIOLATION: [%s (Net %d)] and [%s (Net %d)] distance %.3f mm < required %.3f mm",
                     a->label, a->net_id, b->label, b->net_id, actual_dist, required_clearance);
        }
        return 0;
    }
    return 1;
}
