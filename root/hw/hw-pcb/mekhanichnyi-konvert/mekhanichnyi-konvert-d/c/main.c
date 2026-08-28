#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double nom_enclosure_width;
    double tol_enclosure;
    double nom_pcb_width;
    double tol_pcb_milling;
    double tol_drill_drift;
    double tol_screw_play;
} ToleranceChainInput;

typedef struct {
    double min_clearance_worst_case;
    double min_clearance_rss;
    double max_clearance_worst_case;
    double max_clearance_rss;
    bool is_assemblable;
} ToleranceReport;

ToleranceReport calculate_tolerance_stackup(const ToleranceChainInput* in) {
    ToleranceReport rep;

    double nom_clearance = in->nom_enclosure_width - in->nom_pcb_width;

    /* Метод найгіршого випадку (Worst-Case) */
    double sum_tol_worst = in->tol_enclosure + in->tol_pcb_milling + 
                           in->tol_drill_drift + in->tol_screw_play;

    rep.min_clearance_worst_case = nom_clearance - sum_tol_worst;
    rep.max_clearance_worst_case = nom_clearance + sum_tol_worst;

    /* Статистичний метод RSS (Root Sum Square) */
    double sum_sq = (in->tol_enclosure * in->tol_enclosure) +
                    (in->tol_pcb_milling * in->tol_pcb_milling) +
                    (in->tol_drill_drift * in->tol_drill_drift) +
                    (in->tol_screw_play * in->tol_screw_play);

    double sum_tol_rss = sqrt(sum_sq);

    rep.min_clearance_rss = nom_clearance - sum_tol_rss;
    rep.max_clearance_rss = nom_clearance + sum_tol_rss;

    rep.is_assemblable = (rep.min_clearance_rss > 0.15); /* Технологічний поріг 150 мкм */

    return rep;
}

double calculate_mlcc_safe_radius(double screw_head_radius, double pcb_thickness, double safety_factor) {
    /* R_safe = R_washer + k · T_pcb */
    return screw_head_radius + (safety_factor * pcb_thickness);
}

int main(void) {
    ToleranceChainInput input = {
        .nom_enclosure_width = 122.0, /* мм */
        .tol_enclosure       = 0.25,  /* лиття пластику ±0.25 мм */
        .nom_pcb_width       = 120.0, /* мм */
        .tol_pcb_milling     = 0.15,  /* фрезерування ЧПК ±0.15 мм */
        .tol_drill_drift     = 0.08,  /* зміщення отворів ±0.08 мм */
        .tol_screw_play      = 0.10   /* люфт гвинта в отворі ±0.10 мм */
    };

    ToleranceReport rep = calculate_tolerance_stackup(&input);

    printf("--- АНАЛІЗ РОЗМІРНИХ ЛАНЦЮГІВ ДРУКОВАНОЇ ПЛАТИ ---\n");
    printf("Номінальний зазор: %.2f мм\n", input.nom_enclosure_width - input.nom_pcb_width);
    printf("Worst-Case зазор : [%.3f .. %.3f] мм\n", rep.min_clearance_worst_case, rep.max_clearance_worst_case);
    printf("RSS зазор (3-sigma): [%.3f .. %.3f] мм\n", rep.min_clearance_rss, rep.max_clearance_rss);
    printf("Статус збирання  : %s\n\n", rep.is_assemblable ? "ПРИДАТНО (PASS)" : "РИЗИК ЗАКЛИНЮВАННЯ (FAIL)");

    double r_screw_m3 = 3.0; /* Радіус шайби під M3 = 3.0 мм */
    double t_pcb = 1.6;      /* Товщина FR-4 = 1.6 мм */
    double r_safe = calculate_mlcc_safe_radius(r_screw_m3, t_pcb, 2.5);

    printf("--- РОЗРАХУНОК ЗОНИ БЕЗПЕКИ MLCC (M3 ГВИНТ) ---\n");
    printf("Радіус шайби гвинта : %.2f мм\n", r_screw_m3);
    printf("Товщина діелектрика : %.2f мм\n", t_pcb);
    printf("Безпечний радіус MLCC: %.2f мм (діаметр заборони %.2f мм)\n", r_safe, r_safe * 2.0);

    return 0;
}
