#include <stdio.h>
#include <math.h>

typedef struct {
    double width_mm;
    double height_mm;
    int layer_count;
    double copper_oz;
    double min_trace_mil;
    int quantity;
    int turnaround_hours;
} QuickPcbSpec;

double calculate_quick_estimate(const QuickPcbSpec* s) {
    const double panel_w = 457.0 - 25.0; // 18" мінус поля
    const double panel_h = 610.0 - 25.0; // 24" мінус поля

    int nx = (int)floor((panel_w + 2.0) / (s->width_mm + 2.0));
    int ny = (int)floor((panel_h + 2.0) / (s->height_mm + 2.0));
    int per_panel = (nx > 0 && ny > 0) ? (nx * ny) : 1;

    double layer_factor = 1.0 + 0.45 * (double)(s->layer_count > 2 ? s->layer_count - 2 : 0);
    double cu_factor = 1.0 + 0.40 * (s->copper_oz > 1.0 ? s->copper_oz - 1.0 : 0.0);
    double rush_factor = (s->turnaround_hours <= 48) ? 2.5 : 1.0;

    double panel_base_cost = 45.0 * layer_factor * cu_factor * rush_factor;
    double nre_base = (s->layer_count > 2 ? 150.0 : 60.0) * rush_factor;

    int panels = (s->quantity + per_panel - 1) / per_panel;
    double total = nre_base + (double)panels * panel_base_cost;

    return total / (double)s->quantity;
}
