#include <stdio.h>
#include <math.h>
#include <stdbool.h>

typedef struct {
    double v_rwm;       /* Робоча зворотна напруга, В */
    double v_br;        /* Напруга пробою, В */
    double v_hold;      /* Напруга утримання (для snapback), В */
    double r_dyn;       /* Динамічний опір, Ом */
    double c_j;         /* Паразитна ємність переходу, пФ */
    bool   is_snapback; /* Прапорець структури snapback */
    double l_trace_nh;  /* Паразитна індуктивність доріжки, нГн */
} TvsDevice;

typedef struct {
    double v_clamp_peak; /* Пікова залишкова напруга, В */
    double v_clamp_30ns; /* Залишкова напруга на 30 нс, В */
    double v_inductive;  /* Індуктивний стрибок L * di/dt, В */
    bool   is_safe_for_ic; /* Чи безпечно для кристала IC */
} SimulationResult;

SimulationResult evaluate_esd_protection(const TvsDevice *tvs, double v_esd_kv, double v_max_ic) {
    SimulationResult res;
    
    /* Струм першого піку за IEC 61000-4-2: 3.75 А на кожен кВ */
    double i_peak = v_esd_kv * 3.75;
    double di_dt = i_peak / 0.8; /* Швидкість наростання, А/нс (t_r ≈ 0.8 нс) */
    
    /* Струм другого піку на 30 нс */
    double i_30ns = v_esd_kv * 2.0; 
    
    /* Розрахунок індуктивного стрибка напруги: L (Гн) * (di/dt) (А/с) */
    res.v_inductive = (tvs->l_trace_nh * 1e-9) * (di_dt * 1e9);
    
    /* Розрахунок власної напруги обмеження TVS */
    double v_base = tvs->is_snapback ? tvs->v_hold : tvs->v_br;
    double v_tvs_peak = v_base + (i_peak * tvs->r_dyn);
    
    res.v_clamp_peak = v_tvs_peak + res.v_inductive;
    res.v_clamp_30ns = v_base + (i_30ns * tvs->r_dyn);
    
    res.is_safe_for_ic = (res.v_clamp_peak < v_max_ic);
    return res;
}

int main(void) {
    TvsDevice tvs = {
        .v_rwm = 3.3,
        .v_br = 5.0,
        .v_hold = 3.5,
        .r_dyn = 0.22,
        .c_j = 0.35,
        .is_snapback = true,
        .l_trace_nh = 1.5 /* 1.5 мм доріжки до TVS */
    };
    
    double v_esd = 8.0;   /* Тест 8 кВ контактний розряд */
    double v_ic_max = 12.0; /* Гранична напруга пробою входу IC */
    
    SimulationResult r = evaluate_esd_protection(&tvs, v_esd, v_ic_max);
    
    printf("Результати моделювання захисту при 8 кВ IEC 61000-4-2:\n");
    printf("• Піковий струм розряду: %.1f A\n", v_esd * 3.75);
    printf("• Індуктивний стрибок напруги: %.2f B\n", r.v_inductive);
    printf("• Пікова напруга на вході IC: %.2f B\n", r.v_clamp_peak);
    printf("• Залишкова напруга на 30 нс: %.2f B\n", r.v_clamp_30ns);
    printf("• Статус захисту: %s\n", r.is_safe_for_ic ? "БЕЗПЕЧНО" : "НЕБЕЗПЕКА ПРОБОЮ");
    
    return 0;
}
