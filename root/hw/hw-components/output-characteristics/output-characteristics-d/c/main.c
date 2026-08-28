#include <stdio.h>

/* Структура параметрів каскаду та транзистора */
typedef struct {
    double v_cc;      /* Напруга живлення (В) */
    double r_c;       /* Опір колектора (Ом) */
    double r_e;       /* Опір емітера (Ом) */
    double r_l;       /* Опір навантаження (Ом) */
    double v_a;       /* Напруга Ерлі (В) */
    double v_ce_sat;  /* Напруга насичення (В) */
    double i_cq;      /* Струм спокою колектора (А) */
} StageConfig;

typedef struct {
    double v_ceq;       /* Напруга спокою колектор-емітер (В) */
    double r_ac;        /* Динамічний опір навантаження (Ом) */
    double r_o;         /* Вихідний диференційний опір (Ом) */
    double v_pp_max;    /* Максимальний розмах пік-до-піку (В) */
    int is_clipping_sym;/* Прапорець симетричності розмаху */
} AnalysisResult;

AnalysisResult analyze_bjt_stage(const StageConfig *cfg) {
    AnalysisResult res;
    double r_dc = cfg->r_c + cfg->r_e;
    
    /* Статична напруга спокою за KVL */
    res.v_ceq = cfg->v_cc - cfg->i_cq * r_dc;
    
    /* Динамічний опір навантаження для змінного струму */
    res.r_ac = (cfg->r_c * cfg->r_l) / (cfg->r_c + cfg->r_l);
    
    /* Вихідний опір транзистора з урахуванням ефекту Ерлі */
    res.r_o = (cfg->v_a + res.v_ceq) / cfg->i_cq;
    
    /* Допустимі розмахи плечей до насичення та до відсічки */
    double swing_to_sat = res.v_ceq - cfg->v_ce_sat;
    double swing_to_cut = cfg->i_cq * res.r_ac;
    
    double v_peak_max = (swing_to_sat < swing_to_cut) ? swing_to_sat : swing_to_cut;
    res.v_pp_max = 2.0 * v_peak_max;
    
    /* Перевірка симетричності (допуск 5%) */
    double diff = swing_to_sat - swing_to_cut;
    if (diff < 0) diff = -diff;
    res.is_clipping_sym = (diff / v_peak_max) < 0.05;
    
    return res;
}

int main(void) {
    StageConfig cfg = {
        .v_cc = 12.0,
        .r_c = 1000.0,
        .r_e = 200.0,
        .r_l = 2000.0,
        .v_a = 100.0,
        .v_ce_sat = 0.2,
        .i_cq = 0.005 /* 5 мА */
    };
    
    AnalysisResult res = analyze_bjt_stage(&cfg);
    
    printf("V_CEQ: %.2f V\n", res.v_ceq);
    printf("r_ac:  %.1f Ohm\n", res.r_ac);
    printf("r_o:   %.1f kOhm\n", res.r_o / 1000.0);
    printf("V_pp(max): %.2f V (симетрія: %s)\n", 
           res.v_pp_max, res.is_clipping_sym ? "так" : "ні");
           
    return 0;
}
