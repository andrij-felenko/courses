#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define SPEED_OF_LIGHT_MM_PS 0.299792458  // мм / пс у вакуумі

typedef enum {
    BUS_TYPE_USB2 = 0,
    BUS_TYPE_USB3,
    BUS_TYPE_PCIE_GEN3,
    BUS_TYPE_PCIE_GEN4,
    BUS_TYPE_MIPI_CSI2,
    BUS_TYPE_ETHERNET_1G
} BusStandard_t;

typedef struct {
    const char* name;
    double max_intra_skew_ps; // Максимальний перекіс усередині пари (D+ проти D-)
    double max_inter_skew_ps; // Максимальний перекіс між різними парами (CLK проти Data)
    double target_zdiff_ohm;
    double zdiff_tolerance_pct;
} BusSpec_t;

static const BusSpec_t BUS_SPECS[] = {
    [BUS_TYPE_USB2]        = { "USB 2.0 High Speed",  100.0, 500.0,  90.0, 10.0 },
    [BUS_TYPE_USB3]        = { "USB 3.0 SuperSpeed",   15.0, 100.0,  90.0, 10.0 },
    [BUS_TYPE_PCIE_GEN3]   = { "PCIe Gen3 (8 GT/s)",    5.0,  50.0, 100.0, 10.0 },
    [BUS_TYPE_PCIE_GEN4]   = { "PCIe Gen4 (16 GT/s)",   1.5,  25.0, 100.0, 10.0 },
    [BUS_TYPE_MIPI_CSI2]   = { "MIPI CSI-2 (D-PHY)",    3.0,  10.0, 100.0, 10.0 },
    [BUS_TYPE_ETHERNET_1G] = { "1000Base-T Ethernet",  50.0, 200.0, 100.0, 10.0 },
};

typedef struct {
    double len_p_mm;       // Фізична довжина позитивного провідника
    double len_n_mm;       // Фізична довжина негативного провідника
    double er_effective;   // Ефективна діелектрична проникність шару
    double measured_zdiff; // Виміряний імпеданс лінії (Ом)
} DiffPairMeasurement_t;

typedef struct {
    double intra_skew_ps;
    double delay_p_ps;
    double delay_n_ps;
    bool is_skew_pass;
    bool is_impedance_pass;
} ValidationResult_t;

ValidationResult_t validate_diff_pair(BusStandard_t bus, const DiffPairMeasurement_t* meas) {
    ValidationResult_t res = { 0 };
    const BusSpec_t* spec = &BUS_SPECS[bus];

    double v_prop = SPEED_OF_LIGHT_MM_PS / sqrt(meas->er_effective); // мм / пс
    res.delay_p_ps = meas->len_p_mm / v_prop;
    res.delay_n_ps = meas->len_n_mm / v_prop;
    res.intra_skew_ps = fabs(res.delay_p_ps - res.delay_n_ps);

    res.is_skew_pass = (res.intra_skew_ps <= spec->max_intra_skew_ps);

    double z_min = spec->target_zdiff_ohm * (1.0 - spec->zdiff_tolerance_pct / 100.0);
    double z_max = spec->target_zdiff_ohm * (1.0 + spec->zdiff_tolerance_pct / 100.0);
    res.is_impedance_pass = (meas->measured_zdiff >= z_min && meas->measured_zdiff <= z_max);

    return res;
}

void print_validation_report(BusStandard_t bus, const DiffPairMeasurement_t* meas, const ValidationResult_t* res) {
    const BusSpec_t* spec = &BUS_SPECS[bus];
    printf("====================================================\n");
    printf(" Звіт валідації диференційної пари: %s\n", spec->name);
    printf("====================================================\n");
    printf(" Довжина P / N      : %.3f мм / %.3f мм (ΔL = %.3f мм)\n", 
           meas->len_p_mm, meas->len_n_mm, fabs(meas->len_p_mm - meas->len_n_mm));
    printf(" Затримка P / N     : %.2f пс / %.2f пс\n", res->delay_p_ps, res->delay_n_ps);
    printf(" Фазовий перекіс    : %.2f пс (Ліміт: <= %.2f пс) -> %s\n",
           res->intra_skew_ps, spec->max_intra_skew_ps, res->is_skew_pass ? "PASS" : "FAIL");
    printf(" Імпеданс Z_diff    : %.1f Ом (Ціль: %.1f ± %.0f%%) -> %s\n",
           meas->measured_zdiff, spec->target_zdiff_ohm, spec->zdiff_tolerance_pct,
           res->is_impedance_pass ? "PASS" : "FAIL");
    printf(" Загальний висновок : %s\n", 
           (res->is_skew_pass && res->is_impedance_pass) ? "ГОДЕН ДЛЯ ВИРОБНИЦТВА" : "ПОТРІБНА РЕДАКЦІЯ ТРАСУВАННЯ");
    printf("====================================================\n\n");
}
