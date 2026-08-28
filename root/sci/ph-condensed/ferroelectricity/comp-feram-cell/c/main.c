/* Simulation of 1T-1C FeRAM Read & Write Cycles in C99 */
#include <stdio.h>
#include <math.h>

typedef struct {
    double area_um2;       /* Cell capacitor area in um^2 */
    double P_r_uC_cm2;     /* Remanent polarization P_r at 25C */
    double C_cell_fF;      /* Linear capacitance of cell in fF */
    int stored_state;      /* 0: +Pr ('0'), 1: -Pr ('1') */
} FeramCell;

typedef struct {
    double C_bl_fF;        /* Bit Line parasitic capacitance in fF */
    double V_dd_volts;     /* Read/Write voltage V_DD */
} BitLine;

/* Calculates Signal Margin Delta V_BL in Volts */
double simulate_feram_read(FeramCell* cell, const BitLine* bl, double temp_C, double* v_bl_out) {
    /* Temperature degradation of polarization: P_r(T) = P_r_25 * (1 - 0.0015 * (T - 25)) */
    double p_r_eff = cell->P_r_uC_cm2 * (1.0 - 0.0015 * (temp_C - 25.0));
    if (p_r_eff < 0.0) p_r_eff = 0.0;
    
    double area_cm2 = cell->area_um2 * 1e-8;
    double Q_linear_pC = (cell->C_cell_fF * 1e-3) * bl->V_dd_volts;
    double Q_switch_pC = 0.0;
    
    if (cell->stored_state == 1) {
        /* Reversal of P_s from -Pr to +Pr releases 2 * P_r * Area */
        Q_switch_pC = 2.0 * p_r_eff * (area_cm2 * 1e6);
    }
    
    double Q_total_pC = Q_linear_pC + Q_switch_pC;
    /* V_BL = Q_total / (C_BL + C_cell) */
    double total_cap_fF = bl->C_bl_fF + cell->C_cell_fF;
    *v_bl_out = (Q_total_pC * 1e3) / (total_cap_fF * 1e-3);
    
    /* Destructive read resets cell to state 0 (+Pr) */
    cell->stored_state = 0;
    
    return *v_bl_out;
}

int main(void) {
    FeramCell cell_state_1 = { .area_um2 = 0.05, .P_r_uC_cm2 = 22.0, .C_cell_fF = 12.0, .stored_state = 1 };
    FeramCell cell_state_0 = { .area_um2 = 0.05, .P_r_uC_cm2 = 22.0, .C_cell_fF = 12.0, .stored_state = 0 };
    BitLine bl = { .C_bl_fF = 150.0, .V_dd_volts = 1.8 };
    
    double v_bl_1 = 0.0, v_bl_0 = 0.0;
    simulate_feram_read(&cell_state_1, &bl, 85.0, &v_bl_1); /* Read at 85 C */
    simulate_feram_read(&cell_state_0, &bl, 85.0, &v_bl_0);
    
    printf("FeRAM Read State '1' at 85C: V_BL1 = %.3f V\n", v_bl_1);
    printf("FeRAM Read State '0' at 85C: V_BL0 = %.3f V\n", v_bl_0);
    printf("Sense Window Delta V_BL = %.3f V\n", v_bl_1 - v_bl_0);
    return 0;
}
