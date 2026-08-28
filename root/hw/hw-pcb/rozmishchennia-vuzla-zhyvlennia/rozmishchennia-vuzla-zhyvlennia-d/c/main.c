#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double v_in;        /* Вхідна напруга, В */
    double i_peak;      /* Піковий струм комутації, А */
    double t_sw;        /* Час комутації (наростання/спаду), с */
    double l_loop_nh;   /* Індуктивність петлі, нГн */
    double c_oss_pf;    /* Паразитна ємність транзистора, пФ */
    double area_mm2;    /* Геометрична площа петлі, мм² */
} HotLoopParams;

typedef struct {
    double di_dt;           /* Швидкість зміни струму, А/с */
    double v_spike;         /* Викид перенапруги, В */
    double v_total_peak;    /* Повна напруга на стоці, В */
    double f_ring_mhz;      /* Частота резонансного дзвону, МГц */
    double rel_emi_db;      /* Відносний рівень випромінювання до бази 100 мм² */
} HotLoopResult;

HotLoopResult calculate_hot_loop(const HotLoopParams *p) {
    HotLoopResult res;
    double l_h = p->l_loop_nh * 1e-9;
    double c_f = p->c_oss_pf * 1e-12;
    
    res.di_dt = p->i_peak / p->t_sw;
    res.v_spike = l_h * res.di_dt;
    res.v_total_peak = p->v_in + res.v_spike;
    
    double lc = l_h * c_f;
    if (lc > 0.0) {
        res.f_ring_mhz = (1.0 / (2.0 * M_PI * sqrt(lc))) / 1e6;
    } else {
        res.f_ring_mhz = 0.0;
    }
    
    if (p->area_mm2 > 0.0) {
        res.rel_emi_db = 20.0 * log10(p->area_mm2 / 100.0);
    } else {
        res.rel_emi_db = -100.0;
    }
    
    return res;
}

int main(void) {
    HotLoopParams opt = {
        .v_in = 12.0,
        .i_peak = 10.0,
        .t_sw = 2.0e-9,
        .l_loop_nh = 1.1,
        .c_oss_pf = 350.0,
        .area_mm2 = 12.0
    };
    
    HotLoopResult r = calculate_hot_loop(&opt);
    
    printf("--- Розрахунок оптимізованої гарячої петлі ---\n");
    printf("di/dt:           %.2e A/s\n", r.di_dt);
    printf("V_spike:         %.2f V\n", r.v_spike);
    printf("V_drain_peak:    %.2f V\n", r.v_total_peak);
    printf("f_ringing:       %.1f MHz\n", r.f_ring_mhz);
    printf("Relative EMI:    %.1f dB\n", r.rel_emi_db);
    
    return 0;
}
