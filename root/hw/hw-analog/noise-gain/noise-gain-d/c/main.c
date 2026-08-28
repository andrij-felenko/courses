#include <stdio.h>
#include <math.h>

typedef struct {
    double gbp_hz;       // Добуток підсилення на смугу ОП (Гц)
    double en_nv_rt_hz;  // Власний шум напруги ОП (нВ/√Гц)
    double vos_uv;       // Вхідна напруга зміщення ОП (мкВ)
    double rin_ohm;      // Вхідний резистор (Ом)
    double rf_ohm;       // Резистор зворотного зв'язку (Ом)
    int is_inverting;    // 1 — інвертувальний, 0 — неінвертувальний
} OpAmpCircuit;

typedef struct {
    double signal_gain;      // Підсилення сигналу
    double noise_gain;       // Шумове підсилення NG = 1/beta
    double bandwidth_hz;     // Реальна смуга замкненого кола (Гц)
    double vos_out_uv;       // Вихідне зміщення напруги (мкВ)
    double en_out_nv_rt_hz;  // Вихідна густина шуму від ОП (нВ/√Гц)
} CircuitReport;

CircuitReport calculate_opamp_circuit(const OpAmpCircuit *c) {
    CircuitReport r;
    double ratio = c->rf_ohm / c->rin_ohm;
    
    // Сигнальне підсилення залежить від топології
    if (c->is_inverting) {
        r.signal_gain = -ratio;
    } else {
        r.signal_gain = 1.0 + ratio;
    }
    
    // Шумове підсилення ЗАВЖДИ однакове: 1 + Rf/Rin
    r.noise_gain = 1.0 + ratio;
    
    // Смуга пропускання визначається виключно шумовим підсиленням!
    r.bandwidth_hz = c->gbp_hz / r.noise_gain;
    
    // Вихідна напруга зміщення множиться на шумове підсилення
    r.vos_out_uv = c->vos_uv * r.noise_gain;
    
    // Власний шум напруги ОП множиться на шумове підсилення
    r.en_out_nv_rt_hz = c->en_nv_rt_hz * r.noise_gain;
    
    return r;
}

int main(void) {
    OpAmpCircuit attenuator = {
        .gbp_hz = 10.0e6,     // 10 МГц GBP
        .en_nv_rt_hz = 10.0,  // 10 нВ/√Гц
        .vos_uv = 1000.0,     // 1 мВ (1000 мкВ)
        .rin_ohm = 100000.0,  // 100 кОм
        .rf_ohm = 10000.0,    // 10 кОм
        .is_inverting = 1     // Інвертувальний атенюатор
    };
    
    CircuitReport rep = calculate_opamp_circuit(&attenuator);
    
    printf("Сигнальне підсилення G_сигн : %.2f\n", rep.signal_gain);
    printf("Шумове підсилення NG       : %.2f\n", rep.noise_gain);
    printf("Реальна смуга f_cl         : %.2f кГц\n", rep.bandwidth_hz / 1e3);
    printf("Вихідне зміщення Vos,out   : %.2f мкВ\n", rep.vos_out_uv);
    printf("Вихідний шум ОП en,out     : %.2f нВ/√Гц\n", rep.en_out_nv_rt_hz);
    
    return 0;
}
