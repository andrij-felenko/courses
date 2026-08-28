#include <stdio.h>
#include <stdbool.h>

typedef struct {
    double wire_resistance_ohm;
    double contact_resistance_ohm;
    int contacts_count_per_rail;
    double load_current_a;
    double v_il_max;
    double v_ol_max;
} HarnessParams;

typedef struct {
    double v_drop_loop;
    double ground_shift_v;
    double noise_margin_v;
    bool is_reliable;
} HarnessResult;

HarnessResult calculate_harness(const HarnessParams* p) {
    HarnessResult r;
    double r_rail = p->wire_resistance_ohm + (p->contact_resistance_ohm * p->contacts_count_per_rail);
    double r_loop = 2.0 * r_rail;
    
    r.v_drop_loop = p->load_current_a * r_loop;
    r.ground_shift_v = p->load_current_a * r_rail;
    
    double v_rx_low = p->v_ol_max + r.ground_shift_v;
    r.noise_margin_v = p->v_il_max - v_rx_low;
    r.is_reliable = (r.noise_margin_v >= 0.20) && (r.ground_shift_v <= 0.30);
    return r;
}
