#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Структура параметрів кола постійного струму */
typedef struct {
    double emf_v;         /* ЕРС джерела, Вольти */
    double internal_r;    /* Внутрішній опір джерела r, Оми */
} dc_source_t;

/* Результат розрахунку для точкового опору навантаження */
typedef struct {
    double r_load;        /* Опір навантаження R_L, Оми */
    double ratio_r;       /* Відношення R_L / r */
    double current_a;     /* Струм у колі, Ампери */
    double p_useful_w;    /* Корисна потужність на навантаженні, Вати */
    double p_loss_w;      /* Потужність втрат всередині джерела, Вати */
    double efficiency;    /* Коефіцієнт корисної дії η, відносна величина (0..1) */
} efficiency_point_t;

/* Структура параметрів трансформатора */
typedef struct {
    double nominal_kva;   /* Номінальна повна потужність S_n, кВА */
    double p_core_kw;     /* Постійні втрати в сталі (холостий хід) P_0, кВт */
    double p_copper_kw;   /* Змінні втрати короткого замикання P_sc, кВт */
    double power_factor;  /* Коефіцієнт потужності cos φ */
} transformer_spec_t;

/* Алгоритм скан-аналізу ККД кола постійного струму */
bool analyze_dc_circuit(const dc_source_t* source, double r_start, double r_end, 
                        size_t steps, efficiency_point_t* results) {
    if (!source || !results || steps == 0 || source->internal_r <= 0.0) {
        return false;
    }

    double step_size = (r_end - r_start) / (double)(steps > 1 ? steps - 1 : 1);
    for (size_t i = 0; i < steps; ++i) {
        double r_l = r_start + (double)i * step_size;
        double total_r = r_l + source->internal_r;
        double current = source->emf_v / total_r;

        results[i].r_load = r_l;
        results[i].ratio_r = r_l / source->internal_r;
        results[i].current_a = current;
        results[i].p_useful_w = current * current * r_l;
        results[i].p_loss_w = current * current * source->internal_r;
        results[i].efficiency = results[i].p_useful_w / (results[i].p_useful_w + results[i].p_loss_w);
    }
    return true;
}

/* Обчислення оптимуму ККД трансформатора */
double calculate_transformer_optimal_k(const transformer_spec_t* spec) {
    if (!spec || spec->p_copper_kw <= 0.0 || spec->p_core_kw <= 0.0) {
        return 0.0;
    }
    return sqrt(spec->p_core_kw / spec->p_copper_kw);
}

/* Обчислення ККД трансформатора при заданому коефіцієнті навантаження k */
double calculate_transformer_efficiency(const transformer_spec_t* spec, double k) {
    if (!spec || k < 0.0) {
        return 0.0;
    }
    double p_out = k * spec->nominal_kva * spec->power_factor;
    double p_losses = spec->p_core_kw + (k * k) * spec->p_copper_kw;
    if (p_out + p_losses <= 0.0) {
        return 0.0;
    }
    return p_out / (p_out + p_losses);
}

int main(void) {
    printf("=== СИМУЛЯТОР ТА ОПТИМІЗАТОР ЕЛЕКТРИЧНОГО ККД ===\n\n");

    /* 1. Дослідження режимів кола постійного струму */
    dc_source_t battery = { .emf_v = 12.0, .internal_r = 2.0 };
    const size_t num_points = 5;
    efficiency_point_t points[5];

    if (analyze_dc_circuit(&battery, 0.5, 10.0, num_points, points)) {
        printf("--- Аналіз кола постійного струму (ЕРС = 12В, r = 2 Ом) ---\n");
        printf("R_L (Ом) | R_L/r | Струм (А) | P_кор (Вт) | P_вт (Вт) | ККД (%%)\n");
        printf("----------------------------------------------------------\n");
        for (size_t i = 0; i < num_points; ++i) {
            printf("%7.2f  | %5.2f | %9.2f | %10.2f | %9.2f | %6.2f%%\n",
                   points[i].r_load, points[i].ratio_r, points[i].current_a,
                   points[i].p_useful_w, points[i].p_loss_w, points[i].efficiency * 100.0);
        }
    }

    /* 2. Оптимізація силового трансформатора */
    transformer_spec_t trans = {
        .nominal_kva = 1000.0,
        .p_core_kw = 2.5,
        .p_copper_kw = 10.0,
        .power_factor = 0.90
    };

    double k_opt = calculate_transformer_optimal_k(&trans);
    double max_eta = calculate_transformer_efficiency(&trans, k_opt);
    double nominal_eta = calculate_transformer_efficiency(&trans, 1.0);

    printf("\n--- Аналіз ККД силового трансформатора (1000 кВА) ---\n");
    printf("Постійні втрати P_0: %.2f кВт, Втрати короткого замикання P_sc: %.2f кВт\n",
           trans.p_core_kw, trans.p_copper_kw);
    printf("Оптимальний коефіцієнт навантаження k_opt: %.3f (%.1f%% від номіналу)\n",
           k_opt, k_opt * 100.0);
    printf("Максимальний ККД (при k_opt): %.3f%%\n", max_eta * 100.0);
    printf("Номінальний ККД (при k = 1.0): %.3f%%\n", nominal_eta * 100.0);

    return 0;
}
