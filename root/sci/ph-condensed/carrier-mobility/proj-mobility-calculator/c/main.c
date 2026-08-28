#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Базова константа елементарного заряду у Кулонах */
#define ELEMENTARY_CHARGE 1.602176634e-19

/* Типи напівпровідникових матеріалів */
typedef enum {
    MATERIAL_SILICON,
    MATERIAL_GAAS
} MaterialType;

/* Структура емпіричних параметрів Коугі — Томаса */
typedef struct {
    double mu_min_e;   /* см²/(В·с) */
    double mu_max_e;   /* см²/(В·с) */
    double n_ref_e;    /* см⁻³ */
    double alpha_e;    /* безрозмірний */
    double v_sat_e;    /* см/с */
    double beta_e;     /* безрозмірний */
    double gamma_e;    /* температурний показник */

    double mu_min_h;   /* см²/(В·с) */
    double mu_max_h;   /* см²/(В·с) */
    double n_ref_h;    /* см⁻³ */
    double alpha_h;    /* безрозмірний */
    double v_sat_h;    /* см/с */
    double beta_h;     /* безрозмірний */
    double gamma_h;    /* температурний показник */
} TransportParameters;

/* Результати розрахунку кінетичних параметрів */
typedef struct {
    double mu_e_low;     /* низькопольова рухливість електронів, см²/(В·с) */
    double mu_h_low;     /* низькопольова рухливість дірок, см²/(В·с) */
    double v_drift_e;    /* дрейфова швидкість електронів, см/с */
    double v_drift_h;    /* дрейфова швидкість дірок, см/с */
    double mu_e_field;   /* польова рухливість електронів, см²/(В·с) */
    double mu_h_field;   /* польова рухливість дірок, см²/(В·с) */
    double conductivity; /* питома провідність, 1/(Ом·см) */
    double resistivity;  /* питомий опір, Ом·см */
} MobilityResult;

/* Отримання параметрів матеріалу */
static TransportParameters get_material_parameters(MaterialType mat) {
    TransportParameters p;
    if (mat == MATERIAL_SILICON) {
        /* Електрони в Si */
        p.mu_min_e = 65.0;  p.mu_max_e = 1417.0; p.n_ref_e = 9.68e16;
        p.alpha_e = 0.680;  p.v_sat_e = 1.07e7;  p.beta_e = 1.11; p.gamma_e = 2.42;
        /* Дірки в Si */
        p.mu_min_h = 47.7;  p.mu_max_h = 470.5;  p.n_ref_h = 2.23e17;
        p.alpha_h = 0.719;  p.v_sat_h = 8.37e6;  p.beta_h = 1.21; p.gamma_h = 2.20;
    } else {
        /* Електрони в GaAs */
        p.mu_min_e = 500.0; p.mu_max_e = 8500.0; p.n_ref_e = 1.69e17;
        p.alpha_e = 0.436;  p.v_sat_e = 1.20e7;  p.beta_e = 2.00; p.gamma_e = 1.50;
        /* Дірки в GaAs */
        p.mu_min_h = 20.0;  p.mu_max_h = 400.0;   p.n_ref_h = 2.75e17;
        p.alpha_h = 0.395;  p.v_sat_h = 8.00e6;  p.beta_h = 1.00; p.gamma_h = 1.50;
    }
    return p;
}

/* Розрахунок низькопольової рухливості за моделлю Коугі — Томаса */
static double calc_low_field_mobility(double mu_min, double mu_max, double n_ref, 
                                      double alpha, double gamma, double temp, double n_total) {
    double temp_factor = temp / 300.0;
    double mu_max_t = mu_max * pow(temp_factor, -gamma);
    double mu_min_t = mu_min * pow(temp_factor, -0.5);
    
    if (n_total <= 0.0) {
        return mu_max_t;
    }
    
    double ratio = n_total / n_ref;
    return mu_min_t + (mu_max_t - mu_min_t) / (1.0 + pow(ratio, alpha));
}

/* Розрахунок дрейфової швидкості у сильному полі */
static double calc_drift_velocity(double mu_low, double electric_field, double v_sat, double beta) {
    if (electric_field <= 0.0) {
        return 0.0;
    }
    double field_term = (mu_low * electric_field) / v_sat;
    double denominator = pow(1.0 + pow(field_term, beta), 1.0 / beta);
    return (mu_low * electric_field) / denominator;
}

/* Головна функція обчислення транспортних властивостей */
MobilityResult calculate_carrier_transport(MaterialType mat, double temp_k, 
                                            double n_donor, double n_acceptor, 
                                            double electric_field_v_cm) {
    MobilityResult res;
    TransportParameters p = get_material_parameters(mat);
    double n_total = n_donor + n_acceptor;
    
    /* 1. Низькопольова рухливість */
    res.mu_e_low = calc_low_field_mobility(p.mu_min_e, p.mu_max_e, p.n_ref_e, 
                                          p.alpha_e, p.gamma_e, temp_k, n_total);
    res.mu_h_low = calc_low_field_mobility(p.mu_min_h, p.mu_max_h, p.n_ref_h, 
                                          p.alpha_h, p.gamma_h, temp_k, n_total);
                                          
    /* 2. Дрейфова швидкість та польова рухливість */
    res.v_drift_e = calc_drift_velocity(res.mu_e_low, electric_field_v_cm, p.v_sat_e, p.beta_e);
    res.v_drift_h = calc_drift_velocity(res.mu_h_low, electric_field_v_cm, p.v_sat_h, p.beta_h);
    
    if (electric_field_v_cm > 0.0) {
        res.mu_e_field = res.v_drift_e / electric_field_v_cm;
        res.mu_h_field = res.v_drift_h / electric_field_v_cm;
    } else {
        res.mu_e_field = res.mu_e_low;
        res.mu_h_field = res.mu_h_low;
    }
    
    /* 3. Провідність та питомий опір */
    double free_electrons = n_donor > n_acceptor ? (n_donor - n_acceptor) : 1e10;
    double free_holes = n_acceptor > n_donor ? (n_acceptor - n_donor) : 1e10;
    
    res.conductivity = ELEMENTARY_CHARGE * (free_electrons * res.mu_e_field + free_holes * res.mu_h_field);
    res.resistivity = (res.conductivity > 0.0) ? (1.0 / res.conductivity) : 1e18;
    
    return res;
}

int main(void) {
    printf("=== ДВИГУН ОБЧИСЛЕННЯ РУХЛИВОСТІ НОСІЇВ (C) ===\n\n");
    
    double temp = 300.0; /* K */
    double field = 5000.0; /* В/см */
    double dopings[] = {1e14, 1e16, 1e18, 1e19};
    size_t num_dopings = sizeof(dopings) / sizeof(dopings[0]);
    
    printf("Матеріал: Кремній (Si), T = %.1f K, Поле E = %.1f В/см\n", temp, field);
    printf("----------------------------------------------------------------------------------\n");
    printf("%-12s | %-12s | %-12s | %-14s | %-12s\n", 
           "Допування Nd", "μ_e (см²/Vs)", "μ_h (см²/Vs)", "v_drift_e (см/с)", "Опір (Ом·см)");
    printf("----------------------------------------------------------------------------------\n");
    
    for (size_t i = 0; i < num_dopings; ++i) {
        MobilityResult r = calculate_carrier_transport(MATERIAL_SILICON, temp, dopings[i], 0.0, field);
        printf("%-12.1e | %-12.1f | %-12.1f | %-14.2e | %-12.4f\n", 
               dopings[i], r.mu_e_field, r.mu_h_field, r.v_drift_e, r.resistivity);
    }
    
    return 0;
}
