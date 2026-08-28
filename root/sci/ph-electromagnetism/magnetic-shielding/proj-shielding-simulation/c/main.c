#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define MU_0 (4.0 * M_PI * 1e-7)

typedef struct {
    double r_in;       /* Внутрішній радіус, м */
    double r_out;      /* Зовнішній радіус, м */
    double mu_max;     /* Максимальна відносна проникність */
    double b_sat;      /* Індукція насичення, Тл */
    double n_power;    /* Показник нелінійності */
} ShieldLayer;

/* Обчислення нелінійної проникності за виразом Фреліха-Кеннеллі */
double calc_relative_mu(double b_field, double mu_max, double b_sat, double n_power) {
    if (b_field <= 0.0) return mu_max;
    double ratio = b_field / b_sat;
    if (ratio >= 1.0) return 1.05; /* Практичний мінімум у глибокому насиченні */
    
    double val = 1.0 - pow(ratio, n_power);
    if (val < 0.0) val = 0.0;
    
    double mu_r = 1.0 + (mu_max - 1.0) * val;
    return (mu_r < 1.0) ? 1.0 : mu_r;
}

typedef struct {
    double b_internal;
    double shielding_factor;
    double shielding_db;
    bool is_saturated;
} ShieldResult;

/* Чисельний розрахунок екранування багатошарового циліндра */
ShieldResult simulate_multilayer_shield(const ShieldLayer* layers, size_t count, double b_ext) {
    ShieldResult res;
    res.is_saturated = false;
    
    double current_b = b_ext;
    double total_s = 1.0;
    
    for (size_t i = count; i > 0; i--) {
        size_t idx = i - 1;
        const ShieldLayer* l = &layers[idx];
        
        /* 1. Оцінка індукції у стінці шару за рахунок концентрації потоку */
        double flux_concentration = l->r_out / (l->r_out - l->r_in);
        double b_in_wall = current_b * flux_concentration;
        
        if (b_in_wall >= l->b_sat * 0.9) {
            res.is_saturated = true;
        }
        
        /* 2. Обчислення дійсного значення mu_r з урахуванням нелінійності */
        double mu_r = calc_relative_mu(b_in_wall, l->mu_max, l->b_sat, l->n_power);
        
        /* 3. Окремий коефіцієнт екранування шару S_i */
        double radius_ratio_sq = (l->r_in / l->r_out) * (l->r_in / l->r_out);
        double s_i = 1.0 + 0.25 * ((mu_r - 1.0) * (mu_r - 1.0) / mu_r) * (1.0 - radius_ratio_sq);
        
        /* 4. Формула Кюпфмюллера для геометричного зв'язку шарів */
        if (idx < count - 1) {
            double gap_factor = 1.0 - (l->r_out / layers[idx + 1].r_in) * (l->r_out / layers[idx + 1].r_in);
            total_s *= s_i * gap_factor;
        } else {
            total_s *= s_i;
        }
        
        current_b /= s_i;
    }
    
    res.b_internal = b_ext / total_s;
    res.shielding_factor = total_s;
    res.shielding_db = 20.0 * log10(total_s);
    return res;
}

int main(void) {
    ShieldLayer layers[2] = {
        { .r_in = 0.050, .r_out = 0.051, .mu_max = 150000.0, .b_sat = 0.75, .n_power = 3.0 }, /* Внутрішній мю-метал */
        { .r_in = 0.080, .r_out = 0.082, .mu_max = 10000.0,  .b_sat = 2.00, .n_power = 2.0 }  /* Зовнішня кремниста сталь */
    };
    
    double external_fields[3] = { 50e-6, 1e-3, 10e-3 }; /* 50 мкТл (Земля), 1 мТл, 10 мТл */
    
    printf("=== Чисельне моделювання магнітного екрана (C) ===\n");
    for (int i = 0; i < 3; i++) {
        double b_ext = external_fields[i];
        ShieldResult r = simulate_multilayer_shield(layers, 2, b_ext);
        printf("B_ext = %.2e Тл | B_int = %.2e Тл | S = %.2e (%.1f дБ) | Насичення: %s\n",
               b_ext, r.b_internal, r.shielding_factor, r.shielding_db,
               r.is_saturated ? "ТАК (увага!)" : "НІ");
    }
    
    return 0;
}
