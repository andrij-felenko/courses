/*
 * ground_fault_sim.c — Симуляція струмів замикання та перевірка безпеки (C99)
 */

#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    EARTHING_TN_S,
    EARTHING_TN_C_S,
    EARTHING_TT
} EarthingSystem;

typedef struct {
    double phase_voltage;       /* Фазна напруга (В), наприклад 230.0 */
    double r_trafo;             /* Опір трансформатора (Ом), наприклад 0.05 */
    double r_phase_wire;        /* Опір фазного провідника (Ом) */
    double r_pe_wire;           /* Опір PE/PEN провідника (Ом) */
    double r_source_ground;     /* Опір заземлення нейтралі R0 (Ом), для TT */
    double r_equip_ground;      /* Опір заземлення корпусу Re (Ом), для TT */
    double pe_cross_section_mm2;/* Переріз PE провідника (мм²) */
} GridParameters;

typedef struct {
    double mcb_nominal_current; /* Номінальний струм автомата In (А) */
    char mcb_curve;             /* Тип характеристики: 'B', 'C', або 'D' */
    double rcd_trip_current_ma; /* Струм витоку ПЗВ I_Δn (мА), 0 якщо нема */
    double trip_time_sec;       /* Час спрацьовування захисту (с) */
} ProtectionDevice;

typedef struct {
    double fault_current;       /* Обчислений струм замикання I_f (А) */
    double touch_voltage;       /* Напруга дотику U_touch (В) */
    double min_pe_section_req;  /* Необхідний переріз PE провідника S_min (мм²) */
    bool mcb_tripped_fast;      /* Чи спрацює автомат < 0.4 с */
    bool rcd_tripped;           /* Чи спрацює ПЗВ */
    bool thermal_safe;          /* Перевірка термічної стійкості PE */
    bool safety_passed;         /* Загальний висновок безпеки */
} FaultAnalysisResult;

static double get_mcb_instant_multiplier(char curve) {
    switch (curve) {
        case 'B': return 5.0;
        case 'C': return 10.0;
        case 'D': return 20.0;
        default:  return 10.0;
    }
}

FaultAnalysisResult analyze_ground_fault(EarthingSystem system,
                                        const GridParameters *grid,
                                        const ProtectionDevice *prot) {
    FaultAnalysisResult res = {0};
    double k_cu = 115.0; /* Коефіцієнт термічної стійкості міді */
    
    if (system == EARTHING_TN_S || system == EARTHING_TN_C_S) {
        /* У системах TN струм іде по металевому PE/PEN провіднику */
        double z_loop = grid->r_trafo + grid->r_phase_wire + grid->r_pe_wire;
        if (z_loop <= 0.0001) z_loop = 0.0001;
        
        res.fault_current = grid->phase_voltage / z_loop;
        res.touch_voltage = res.fault_current * grid->r_pe_wire;
        
        double trip_threshold = prot->mcb_nominal_current * 
                                get_mcb_instant_multiplier(prot->mcb_curve);
        res.mcb_tripped_fast = (res.fault_current >= trip_threshold);
        res.rcd_tripped = (prot->rcd_trip_current_ma > 0 && 
                           (res.fault_current * 1000.0) >= prot->rcd_trip_current_ma);
        
        /* Розрахунок термічної стійкості PE провідника */
        double t_trip = res.mcb_tripped_fast ? 0.02 : prot->trip_time_sec;
        res.min_pe_section_req = (res.fault_current * sqrt(t_trip)) / k_cu;
        res.thermal_safe = (grid->pe_cross_section_mm2 >= res.min_pe_section_req);
        
        res.safety_passed = (res.mcb_tripped_fast || res.rcd_tripped) && res.thermal_safe;
        
    } else if (system == EARTHING_TT) {
        /* У системі TT струм замикається через землю (R_e + R_0) */
        double z_loop = grid->r_trafo + grid->r_phase_wire + 
                        grid->r_equip_ground + grid->r_source_ground;
        
        res.fault_current = grid->phase_voltage / z_loop;
        res.touch_voltage = res.fault_current * grid->r_equip_ground;
        
        double trip_threshold = prot->mcb_nominal_current * 
                                get_mcb_instant_multiplier(prot->mcb_curve);
        res.mcb_tripped_fast = (res.fault_current >= trip_threshold);
        
        if (prot->rcd_trip_current_ma > 0) {
            double rcd_trip_a = prot->rcd_trip_current_ma / 1000.0;
            res.rcd_tripped = (res.fault_current >= rcd_trip_a);
            bool voltage_safe = (grid->r_equip_ground * rcd_trip_a) <= 50.0;
            
            double t_trip = 0.03; /* Типовий час спрацювання ПЗВ 30 мс */
            res.min_pe_section_req = (res.fault_current * sqrt(t_trip)) / k_cu;
            res.thermal_safe = (grid->pe_cross_section_mm2 >= res.min_pe_section_req);
            
            res.safety_passed = res.rcd_tripped && voltage_safe && res.thermal_safe;
        } else {
            res.rcd_tripped = false;
            res.thermal_safe = false;
            res.safety_passed = false;
        }
    }
    
    return res;
}

void print_result(const char *title, FaultAnalysisResult res) {
    printf("=== %s ===\n", title);
    printf("Струм замикання I_f:   %.2f А\n", res.fault_current);
    printf("Напруга дотику U_t:    %.2f В\n", res.touch_voltage);
    printf("Необхідний переріз PE: %.2f мм²\n", res.min_pe_section_req);
    printf("Швидке вимкнення MCB:  %s\n", res.mcb_tripped_fast ? "ТАК" : "НІ");
    printf("Спрацювання ПЗВ (RCD): %s\n", res.rcd_tripped ? "ТАК" : "НІ");
    printf("Термічна стійкість PE: %s\n", res.thermal_safe ? "НОРМА" : "ПЕРЕГРІВ!");
    printf("Статус безпеки:        %s\n\n", 
           res.safety_passed ? "БЕЗПЕЧНО (НОРМА)" : "НЕБЕЗПЕЧНО (АВАРІЯ!)");
}

int main(void) {
    GridParameters grid_tn = {
        .phase_voltage = 230.0,
        .r_trafo = 0.05,
        .r_phase_wire = 0.35,  /* 25 м кабелю 1.5 мм² Cu */
        .r_pe_wire = 0.35,
        .r_source_ground = 2.0,
        .r_equip_ground = 4.0,
        .pe_cross_section_mm2 = 1.5
    };
    
    ProtectionDevice prot_mcb_16c = {
        .mcb_nominal_current = 16.0,
        .mcb_curve = 'C',      /* Порог відключення: 160 А */
        .rcd_trip_current_ma = 30.0,
        .trip_time_sec = 0.4
    };
    
    FaultAnalysisResult res_tn = analyze_ground_fault(EARTHING_TN_S, &grid_tn, &prot_mcb_16c);
    print_result("Симуляція замикання у системі TN-S", res_tn);
    
    GridParameters grid_tt = grid_tn;
    grid_tt.r_equip_ground = 15.0; /* Опір контуру приватного будинку 15 Ом */
    
    FaultAnalysisResult res_tt = analyze_ground_fault(EARTHING_TT, &grid_tt, &prot_mcb_16c);
    print_result("Симуляція замикання у системі TT (з ПЗВ 30 мА)", res_tt);
    
    ProtectionDevice prot_no_rcd = prot_mcb_16c;
    prot_no_rcd.rcd_trip_current_ma = 0; /* ПЗВ відсутнє */
    
    FaultAnalysisResult res_tt_bad = analyze_ground_fault(EARTHING_TT, &grid_tt, &prot_no_rcd);
    print_result("Симуляція замикання у системі TT (БЕЗ ПЗВ)", res_tt_bad);
    
    return 0;
}
