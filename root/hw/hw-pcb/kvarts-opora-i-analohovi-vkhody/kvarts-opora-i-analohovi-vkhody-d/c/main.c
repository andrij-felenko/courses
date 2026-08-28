#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double freq_hz;          /* Номінальна частота, Гц */
    double load_cap_pf;      /* Паспортна ємність навантаження CL, пФ */
    double esr_ohm;          /* Еквівалентний послідовний опір ESR, Ом */
    double shunt_cap_pf;     /* Статична ємність C0, пФ */
    double drive_level_max_uw; /* Максимальна потужність збудження, мкВт */
} CrystalParams;

typedef struct {
    double gm_uA_per_V;      /* Крутизна інвертора gm, мкА/В */
    double vdd_volts;        /* Напруга живлення генератора, В */
    double pcb_stray_pf;     /* Паразитна ємність монтажу C_stray, пФ */
} McuOscParams;

typedef struct {
    double c_ext_pf;         /* Рекомендований номінал C1 = C2, пФ */
    double gm_crit_uA_per_V; /* Критична крутизна, мкА/В */
    double gain_margin;      /* Запас по підсиленню */
    double rd_opt_ohm;       /* Оптимальний демпфуючий опір Rd, Ом */
    bool is_osc_safe;        /* Прапорець надійності запуску */
} CrystalCalcResult;

bool calculate_crystal_network(const CrystalParams *xtal,
                               const McuOscParams *mcu,
                               CrystalCalcResult *res)
{
    if (!xtal || !mcu || !res || xtal->load_cap_pf <= mcu->pcb_stray_pf) {
        return false;
    }

    /* 1. Розрахунок зовнішніх конденсаторів C1 = C2 = 2 * (CL - C_stray) */
    res->c_ext_pf = 2.0 * (xtal->load_cap_pf - mcu->pcb_stray_pf);

    /* 2. Розрахунок критичної крутизни gm_crit = 4 * ESR * (2*pi*f)^2 * (C0 + CL)^2 */
    double omega = 2.0 * M_PI * xtal->freq_hz;
    double c_total_f = (xtal->shunt_cap_pf + xtal->load_cap_pf) * 1e-12;
    double gm_crit_si = 4.0 * xtal->esr_ohm * (omega * omega) * (c_total_f * c_total_f);
    res->gm_crit_uA_per_V = gm_crit_si * 1e6;

    /* 3. Запас по підсиленню Gain Margin = gm / gm_crit */
    res->gain_margin = mcu->gm_uA_per_V / res->gm_crit_uA_per_V;
    res->is_osc_safe = (res->gain_margin >= 5.0);

    /* 4. Оптимальний опір Rd = 1 / (2 * pi * f * C2) */
    double c2_f = res->c_ext_pf * 1e-12;
    res->rd_opt_ohm = 1.0 / (omega * c2_f);

    return true;
}

int main(void)
{
    CrystalParams hse = {
        .freq_hz = 16000000.0,       /* 16 МГц */
        .load_cap_pf = 12.0,         /* CL = 12 пФ */
        .esr_ohm = 30.0,             /* ESR = 30 Ом */
        .shunt_cap_pf = 3.0,         /* C0 = 3 пФ */
        .drive_level_max_uw = 100.0  /* P_max = 100 мкВт */
    };

    McuOscParams stm32 = {
        .gm_uA_per_V = 3000.0,       /* gm = 3.0 мА/В = 3000 мкА/В */
        .vdd_volts = 3.3,
        .pcb_stray_pf = 3.5          /* C_stray = 3.5 пФ */
    };

    CrystalCalcResult res;
    if (calculate_crystal_network(&hse, &stm32, &res)) {
        printf("HSE 16 МГц розрахунок контуру:\n");
        printf("  C1, C2 номінал:     %.2f пФ (рекомендовано 18 пФ C0G)\n", res.c_ext_pf);
        printf("  gm_crit:            %.2f мкА/В\n", res.gm_crit_uA_per_V);
        printf("  Gain Margin:        %.2f (критерій >= 5: %s)\n",
               res.gain_margin, res.is_osc_safe ? "ВИКОНАНО" : "НЕБЕЗПЕКА");
        printf("  Оптимальний Rd:     %.1f Ом\n", res.rd_opt_ohm);
    }
    return 0;
}
